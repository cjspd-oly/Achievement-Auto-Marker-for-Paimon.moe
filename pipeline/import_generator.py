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


def ensure_directory_exists(path):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def log(message: str, enabled: bool = True):
    if enabled:
        print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def load_main_config(main_config_path: str) -> dict:
    if not os.path.exists(main_config_path):
        raise FileNotFoundError(f"Main config file not found: {main_config_path}")
    return toml.load(main_config_path)


def load_step_config(step_config_path: str, main_config_path: str) -> dict:
    if not os.path.exists(step_config_path):
        log(f"Step config not found at {step_config_path}, creating default.", True)
        create_default_config(step_config_path, main_config_path)
    return toml.load(step_config_path)


def create_default_config(config_path: str, main_config_path: str):
    main_config = load_main_config(main_config_path)
    ocr_config_path = main_config["steps"].get("ocr_extraction", "")

    if not os.path.exists(ocr_config_path):
        raise FileNotFoundError("OCR config path does not exist. Run OCR step first.")

    ocr_config = toml.load(ocr_config_path)
    titles_file = ocr_config.get("output", {}).get("all_titles_file", None)

    default_config = {
        "input": {
            "titles_file": titles_file,
            "db_file": "paimon_data/db.json",
            "import_file": "paimon_data/raw.json",
        },
        "output": {
            "error_file": f"data/error/{STEP_NAME}_mismatch_{TIMESTAMP}.txt",
            "final_import_file": f"uploads/upload{TIMESTAMP}.json",
        },
        "settings": {"threshold": 90, "verbose": True},
    }

    ensure_directory_exists(os.path.dirname(config_path))
    with open(config_path, "w") as f:
        toml.dump(default_config, f)
    print(f"Default config created at: {config_path}")


def match_and_update_import(config):
    titles_file = config["input"]["titles_file"]
    db_file = config["input"]["db_file"]
    import_file = config["input"]["import_file"]
    error_file = config["output"]["error_file"]
    final_import_file = config["output"]["final_import_file"]
    threshold = config["settings"].get("threshold", 90)
    verbose = config["settings"].get("verbose", True)

    for path in [titles_file, db_file, import_file]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")

    with open(titles_file, "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]

    with open(db_file, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    with open(import_file, "r", encoding="utf-8") as f:
        import_data = json.load(f)

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

            for key in import_data.get("achievement", {}):
                if str(matched_id) in import_data["achievement"][key]:
                    import_data["achievement"][key][str(matched_id)] = True

            for checklist_id, checklist_items in import_data.get(
                "achievement-checklist", {}
            ).items():
                if str(matched_id) == checklist_id:
                    for sub_id in checklist_items:
                        import_data["achievement-checklist"][checklist_id][sub_id] = (
                            sub_id == "0"
                        )

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


def run_from_config(main_config_path: str):
    try:
        ensure_directory_exists(LOG_DIR)
        main_config = load_main_config(main_config_path)
        step_config_path = main_config["steps"].get(STEP_NAME)
        config = load_step_config(step_config_path, main_config_path)
        match_and_update_import(config)
    except Exception as e:
        log(f"[Fatal Error] {e}", True)
        sys.exit(1)


if __name__ == "__main__":
    run_from_config("config/main_config.toml")
