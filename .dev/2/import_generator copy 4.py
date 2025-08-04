import json
import os
import toml
import sys
from datetime import datetime
from rapidfuzz.fuzz import token_sort_ratio, token_set_ratio, ratio

STEP_NAME = "import_generator"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"{STEP_NAME}_{TIMESTAMP}.log")
MERGE_LOG_FILE = os.path.join(LOG_DIR, f"{STEP_NAME}_merge_{TIMESTAMP}.log")

MERGE_SUMMARY = {"updates": 0}
MERGE_UPDATED_IDS = set()

def ensure_directory_exists(path):
    if path and isinstance(path, str) and path.strip():
        try:
            os.makedirs(path, exist_ok=True)
        except (FileNotFoundError, OSError):
            pass

def log(message: str, enabled: bool = True, merge: bool = False):
    if enabled:
        print(message)
    log_path = MERGE_LOG_FILE if merge else LOG_FILE
    ensure_directory_exists(os.path.dirname(log_path))
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def log_merge_summary():
    if MERGE_SUMMARY["updates"] > 0:
        log(f"\n[Merged] Total updated entries: {MERGE_SUMMARY['updates']}", merge=True)
    else:
        log("[Merged] No updates were made.", merge=True)

def load_main_config(main_config_path: str) -> dict:
    if not os.path.exists(main_config_path):
        raise FileNotFoundError(f"Main config file not found: {main_config_path}")
    return toml.load(main_config_path)

def load_step_config(step_config_path: str, main_config_path: str) -> dict:
    if not os.path.exists(step_config_path):
        log(f"Step config not found at {step_config_path}, creating default.", True)
        create_default_config(step_config_path, main_config_path)
    return toml.load(step_config_path)

def get_latest_file_from_dirs(dirs):
    all_files = []
    for d in dirs:
        if os.path.exists(d):
            all_files.extend(
                os.path.join(d, f)
                for f in os.listdir(d)
                if f.lower().endswith(".json")
            )
    return max(all_files, key=os.path.getctime) if all_files else None

def create_default_config(config_path: str, main_config_path: str):
    uploads_dir = "uploads"
    merged_dir = "merged_uploads"
    user_partial_dir = "user_partial_uploads"

    ensure_directory_exists(merged_dir)
    ensure_directory_exists(user_partial_dir)

    uploaded_file_path = None
    merge_mode = False

    user_choice = {
        "use_downloaded_file": True,
        "use_uploaded_file": False,
        "create_new_upload": True
    }

    if user_choice["use_downloaded_file"]:
        file_path = get_latest_file_from_dirs([user_partial_dir])
        if file_path:
            uploaded_file_path = file_path
            merge_mode = True
            print(f"Using user partial download: {uploaded_file_path}")
            user_choice = {"use_downloaded_file": False, "use_uploaded_file": True, "create_new_upload": False}

    if not uploaded_file_path and user_choice["use_uploaded_file"]:
        file_path = get_latest_file_from_dirs([merged_dir, uploads_dir])
        if file_path:
            uploaded_file_path = file_path
            merge_mode = True
            print(f"Using last uploaded: {uploaded_file_path}")

    if not uploaded_file_path and user_choice["create_new_upload"]:
        fallback_file = "paimon_data/raw.json"
        if os.path.exists(fallback_file):
            uploaded_file_path = os.path.join(merged_dir, f"initial_upload_{TIMESTAMP}.json")
            with open(fallback_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            with open(uploaded_file_path, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=4)
            latest_file = os.path.join(merged_dir, "latest.json")
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=4)
            uploaded_file_path = latest_file
            merge_mode = True
            print(f"Created fresh upload from raw.json -> {uploaded_file_path}")

    if not uploaded_file_path:
        fallback_file = "paimon_data/raw.json"
        if os.path.exists(fallback_file):
            uploaded_file_path = fallback_file
            merge_mode = False
            print(f"Fallback: Using paimon_data/raw.json directly -> {uploaded_file_path}")

    if not uploaded_file_path or not os.path.exists(uploaded_file_path):
        raise FileNotFoundError("No valid file found from any configured choice.")

    titles_file = None
    try:
        main_config = load_main_config(main_config_path)
        ocr_config_path = main_config.get("steps", {}).get("ocr_extraction", "")
        if ocr_config_path and os.path.exists(ocr_config_path):
            ocr_config = toml.load(ocr_config_path)
            titles_file = ocr_config.get("output", {}).get("all_titles_file", None)
    except Exception as e:
        print(f"[Warning] Failed to extract titles from OCR config: {e}")

    default_config = {
        "input": {
            "titles_file": titles_file,
            "db_file": "paimon_data/db.json",
            "import_file": "paimon_data/raw.json",
            "uploaded_file": uploaded_file_path,
            "uploaded_file_dir": merged_dir,
        },
        "output": {
            "error_file": f"data/error/{STEP_NAME}_mismatch_{TIMESTAMP}.txt",
            "final_import_file": f"uploads/upload{TIMESTAMP}.json",
        },
        "settings": {
            "threshold": 90,
            "verbose": True,
            "merge_uploads": merge_mode,
            "choice_use_downloaded_file": user_choice["use_downloaded_file"],
            "choice_use_uploaded_file": user_choice["use_uploaded_file"],
            "choice_create_new_upload": user_choice["create_new_upload"]
        },
    }

    ensure_directory_exists(os.path.dirname(config_path))
    with open(config_path, "w") as f:
        toml.dump(default_config, f)
    print(f"Default config created at: {config_path}")



def load_step_config(step_config_path: str, main_config_path: str) -> dict:
    if not os.path.exists(step_config_path):
        log(f"Step config not found at {step_config_path}, creating default.", True)
        create_default_config(step_config_path, main_config_path)
    return toml.load(step_config_path)


# all other functions remain unchanged — no need to modify smart_merge_imports, match_and_update_import, etc.
def smart_merge_imports(current_data: dict, uploaded_data: dict) -> dict:
    def walk_paths(data, prefix=[]):
        if isinstance(data, dict):
            for key, value in data.items():
                yield from walk_paths(value, prefix + [key])
        else:
            yield prefix, data

    def get_nested(d, keys):
        for key in keys:
            if not isinstance(d, dict) or key not in d:
                return None
            d = d[key]
        return d

    def set_nested(d, keys, value):
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    for keys, value in walk_paths(uploaded_data):
        if value is True:
            existing_val = get_nested(current_data, keys)
            if existing_val is not True:
                set_nested(current_data, keys, True)
                path_str = "->".join(keys)
                action = "Created" if existing_val is None else "Updated"
                log(f"{action} {path_str} = True", merge=True)
                MERGE_UPDATED_IDS.add(path_str)
                MERGE_SUMMARY["updates"] += 1

    log_merge_summary()
    return current_data

def match_and_update_import(config):
    titles_file = config["input"]["titles_file"]
    db_file = config["input"]["db_file"]
    import_file = config["input"]["import_file"]
    error_file = config["output"]["error_file"]
    final_import_file = config["output"]["final_import_file"]
    threshold = config["settings"].get("threshold", 90)
    verbose = config["settings"].get("verbose", True)
    merge_uploads = config["settings"].get("merge_uploads", False)
    uploaded_file = config["input"].get("uploaded_file")

    for path in [titles_file, db_file, import_file]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")

    with open(titles_file, "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]

    with open(db_file, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    with open(import_file, "r", encoding="utf-8") as f:
        import_data = json.load(f)

    if merge_uploads:
        merged_dir = "merged_uploads"
        ensure_directory_exists(merged_dir)

        if not uploaded_file:
            files = [f for f in os.listdir(merged_dir) if f.endswith(".json")]
            if files:
                uploaded_file = max(
                    (os.path.join(merged_dir, f) for f in files),
                    key=os.path.getctime,
                    default=None,
                )
        if uploaded_file and os.path.exists(uploaded_file):
            log(f"[MERGE] Merging from uploaded file: {uploaded_file}", verbose)
            with open(uploaded_file, "r", encoding="utf-8") as f:
                uploaded_data = json.load(f)
            import_data = smart_merge_imports(import_data, uploaded_data)
        else:
            log(f"[Warning] No valid uploaded file found for merging.", True)
            merge_uploads = False

    achievement_list = []
    for category in db_data.values():
        achievements = category.get("achievements", [])
        for entry in achievements:
            if isinstance(entry, dict):
                achievement_list.append(entry)
            elif isinstance(entry, list):
                achievement_list.extend(entry)

    id_to_name = {
        a["id"]: a["name"] for a in achievement_list if "id" in a and "name" in a
    }
    name_list = list(id_to_name.values())
    id_list = list(id_to_name.keys())

    ensure_directory_exists(os.path.dirname(error_file))
    with open(error_file, "w", encoding="utf-8") as ef:
        ef.write("")

    def get_best_match(title):
        scores = []
        for name in name_list:
            s1 = token_set_ratio(title, name)
            s2 = token_sort_ratio(title, name)
            s3 = ratio(title, name)
            best = max(s1, s2, s3)
            scores.append((name, best, s1, s2, s3))
        best_match = max(scores, key=lambda x: x[1])
        return best_match if best_match[1] >= threshold else None

    matched_count, unmatched_count = 0, 0

    for title in titles:
        best_match = get_best_match(title)
        if best_match:
            matched_name = best_match[0]
            matched_id = id_list[name_list.index(matched_name)]
            matched_score = best_match[1]
            matched_count += 1

            log(
                f"[MATCH] '{title}' → '{matched_name}' (ID: {matched_id}) Score: {matched_score} "
                f"| set_ratio={best_match[2]} sort_ratio={best_match[3]} ratio={best_match[4]}",
                verbose,
            )

            if "achievement" not in import_data or not isinstance(
                import_data["achievement"], dict
            ):
                import_data["achievement"] = {}
            if "0" not in import_data["achievement"] or not isinstance(
                import_data["achievement"]["0"], dict
            ):
                import_data["achievement"]["0"] = {}

            ach = import_data["achievement"]["0"]
            if str(matched_id) not in ach or not ach[str(matched_id)]:
                ach[str(matched_id)] = True

            checklist = import_data.get("achievement-checklist", {})
            if str(matched_id) in checklist and isinstance(
                checklist[str(matched_id)], dict
            ):
                if (
                    "0" in checklist[str(matched_id)]
                    and not checklist[str(matched_id)]["0"]
                ):
                    checklist[str(matched_id)]["0"] = True
        else:
            log(f"[NO MATCH] '{title}'", verbose)
            unmatched_count += 1
            with open(error_file, "a", encoding="utf-8") as ef:
                ef.write(title + "\n")

    ensure_directory_exists(os.path.dirname(final_import_file))
    with open(final_import_file, "w", encoding="utf-8") as f:
        json.dump(import_data, f, indent=4, ensure_ascii=False)

    log("\n=== DONE ===", True)
    log(f"Total Titles: {len(titles)}", True)
    log(f"Matched: {matched_count}", True)
    log(f"Unmatched: {unmatched_count}", True)
    log(f"Errors written to: {error_file}", True)
    log(f"Final import file saved at: {final_import_file}", True)
###

def run_from_config(main_config_path: str):
    try:
        ensure_directory_exists(LOG_DIR)
        if not os.path.exists(main_config_path):
            raise FileNotFoundError(f"Main config path not found: {main_config_path}")
        main_config = load_main_config(main_config_path)
        step_config_path = main_config.get("steps", {}).get(STEP_NAME)
        if not step_config_path:
            raise ValueError(f"No step config path defined for step '{STEP_NAME}' in main config.")
        config = load_step_config(step_config_path, main_config_path)
        match_and_update_import(config)
    except Exception as e:
        log(f"[Fatal Error] {e}", True)
        sys.exit(1)


if __name__ == "__main__":
    run_from_config("config/main_config.toml")
