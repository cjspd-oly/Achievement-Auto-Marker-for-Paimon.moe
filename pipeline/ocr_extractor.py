import easyocr
import os
import time
import toml
import sys
from collections import OrderedDict
from datetime import datetime

STEP_NAME = "ocr_extraction"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory_exists(path):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def load_main_config(main_config_path: str) -> dict:
    if not os.path.exists(main_config_path):
        raise FileNotFoundError(f"Main config file not found at {main_config_path}")
    return toml.load(main_config_path)


def load_step_config(step_config_path: str, main_config_path: str) -> dict:
    if not os.path.exists(step_config_path):
        log(f"Step config not found at {step_config_path}, creating default.", True)
        create_default_config(step_config_path, main_config_path)
    return toml.load(step_config_path)


def create_default_config(config_path: str, main_config_path: str):
    main_config = load_main_config(main_config_path)
    frame_config_path = main_config["steps"].get("frame_extraction", "")

    if not os.path.exists(frame_config_path):
        raise FileNotFoundError(f"Frame config path not found: {frame_config_path}")

    frame_config = toml.load(frame_config_path)
    frame_output_folder = frame_config.get("output", {}).get("folder", "")

    if not os.path.exists(frame_output_folder):
        raise FileNotFoundError(
            f"Frame extraction output folder not found: {frame_output_folder}"
        )

    input_folder = frame_output_folder
    output_folder = f"data/ocr/{STEP_NAME}_{TIMESTAMP}"
    all_titles_path = None

    default_config = {
        "input": {"folder": input_folder},
        "output": {"folder": output_folder, "all_titles_file": all_titles_path},
        "settings": {"language": ["en"], "verbose": True},
    }
    ensure_directory_exists(os.path.dirname(config_path) or ".")
    with open(config_path, "w") as f:
        toml.dump(default_config, f)
    print(f"Default config created at: {config_path}")


# Logging setup
LOG_DIR = "logs"
ensure_directory_exists(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, f"{STEP_NAME}_{TIMESTAMP}.log")


def log(message: str, enabled: bool = True):
    if enabled:
        print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def extract_titles_from_images(config: dict):
    input_folder = config["input"]["folder"]
    output_folder = config["output"]["folder"]
    languages = config["settings"].get("language", ["en"])
    verbose = config["settings"].get("verbose", True)

    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    ensure_directory_exists(output_folder)
    reader = easyocr.Reader(languages)
    combined_titles = OrderedDict()
    image_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not image_files:
        raise FileNotFoundError(f"No images found in folder: {input_folder}")

    start_time = time.time()

    for img_file in image_files:
        img_path = os.path.join(input_folder, img_file)
        log(f"Processing {img_file}...", verbose)

        result = reader.readtext(img_path)
        lines = [detection[1].strip() for detection in result]

        raw_text_file = os.path.join(
            output_folder, f"{os.path.splitext(img_file)[0]}_raw.txt"
        )
        with open(raw_text_file, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

    # Post-process titles after all OCR is done
    for img_file in image_files:
        raw_text_file = os.path.join(
            output_folder, f"{os.path.splitext(img_file)[0]}_raw.txt"
        )
        if not os.path.exists(raw_text_file):
            continue
        with open(raw_text_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        titles = []
        for i in range(1, len(lines)):
            if lines[i] == "Completed":
                title = lines[i - 1]
                titles.append(title)
                combined_titles[title] = None

        titles_file = os.path.join(
            output_folder, f"{os.path.splitext(img_file)[0]}_titles.txt"
        )
        with open(titles_file, "w", encoding="utf-8") as f:
            for title in titles:
                f.write(title + "\n")

    combined_titles_file = os.path.join(output_folder, "all_titles.txt")
    with open(combined_titles_file, "w", encoding="utf-8") as f:
        for title in combined_titles:
            f.write(title + "\n")

    config["output"]["all_titles_file"] = combined_titles_file

    main_config_path = config.get("_main_config_path", "")
    if main_config_path:
        main_config = load_main_config(main_config_path)
        ocr_config_path = main_config["steps"].get("ocr_extraction")
        if ocr_config_path:
            with open(ocr_config_path, "w") as f:
                toml.dump({k: v for k, v in config.items() if not k.startswith("_")}, f)

    end_time = time.time()
    total_time_sec = end_time - start_time
    avg_time_sec = total_time_sec / len(image_files)

    log("\n=== OCR Summary ===", True)
    log(f"Processed {len(image_files)} images.", True)
    log(f"Total time: {format_time(total_time_sec)}", True)
    log(f"Avg time/image: {format_time(avg_time_sec)}", True)
    log(f"Titles saved to: {combined_titles_file}", True)


def run_from_config(main_config_path: str):
    try:
        main_config = load_main_config(main_config_path)
        ocr_config_path = main_config["steps"].get("ocr_extraction")
        config = load_step_config(ocr_config_path, main_config_path)
        config["_main_config_path"] = main_config_path

        extract_titles_from_images(config)

    except Exception as e:
        log(f"[Fatal Error] {e}", True)
        sys.exit(1)


if __name__ == "__main__":
    run_from_config("config/main_config.toml")
