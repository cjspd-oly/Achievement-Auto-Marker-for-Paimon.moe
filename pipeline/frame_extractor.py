import cv2
import os
import numpy as np
import time
import toml
from datetime import datetime
import sys

STEP_NAME = "frame_extraction"
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_DIR = "logs"
MAIN_CONFIG_PATH = "config/main_config.toml"


def ensure_directory_exists(path):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


ensure_directory_exists(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, f"{STEP_NAME}_{TIMESTAMP}.log")


def load_main_config(main_config_path: str) -> dict:
    if not os.path.exists(main_config_path):
        raise FileNotFoundError(f"Main config file not found: {main_config_path}")
    return toml.load(main_config_path)


def load_step_config(step_config_path: str, main_config_path: str) -> dict:
    if not os.path.exists(step_config_path):
        create_default_config(step_config_path)
    return toml.load(step_config_path)


def create_default_config(config_path: str):
    default_config = {
        "video": {
            "path": "sample.mp4"
        },
        "output": {
            "folder": f"data/frames/{STEP_NAME}_{TIMESTAMP}"
        },
        "settings": {
            "diff_threshold": 1000000,
            "save_first_frame": True,
            "verbose": True,
            "log_skipped_frames": False,
            "save_gray_diff_map": False
        }
    }
    ensure_directory_exists(os.path.dirname(config_path))
    with open(config_path, "w") as f:
        toml.dump(default_config, f)
    print(f"Default config created at: {config_path}")


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def log(message: str, enabled: bool = True):
    if enabled:
        print(message)
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')


def print_summary(frame_num: int, saved_frame_num: int, start_time: float, end_time: float):
    summary = (
        "\n=== Summary ===\n"
        f"Total frames scanned: {frame_num}\n"
        f"Unique frames saved: {saved_frame_num}\n"
        f"Total time: {format_time(end_time - start_time)}\n"
        "================"
    )
    log(summary)


def extract_unique_frames(
    video_path: str,
    output_folder: str,
    diff_threshold: float,
    save_first_frame: bool = True,
    verbose: bool = True,
    log_skipped_frames: bool = False,
    save_gray_diff_map: bool = False
):
    ensure_directory_exists(output_folder)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Failed to open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    log(f"Video: {video_path}", verbose)
    log(f"Total frames: {total_frames}", verbose)
    log(f"FPS: {fps:.2f}", verbose)

    frame_num = 0
    saved_frame_num = 0
    prev_gray = None

    start_time = time.time()

    while cap.isOpened():
        try:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is None and save_first_frame:
                output_path = os.path.join(output_folder, f'frame_{saved_frame_num:04}.png')
                cv2.imwrite(output_path, frame)
                log(f"[{saved_frame_num}] Saved first frame.", verbose)
                saved_frame_num += 1
            elif prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                diff_score = np.sum(diff)

                if diff_score > diff_threshold:
                    output_path = os.path.join(output_folder, f'frame_{saved_frame_num:04}.png')
                    cv2.imwrite(output_path, frame)
                    log(f"[{saved_frame_num}] Saved frame — diff: {diff_score}", verbose)
                    if save_gray_diff_map:
                        diff_map_path = os.path.join(output_folder, f'diff_{saved_frame_num:04}.png')
                        cv2.imwrite(diff_map_path, diff)
                    saved_frame_num += 1
                else:
                    log(f"[{frame_num}] Skipped — diff: {diff_score}", log_skipped_frames)

            prev_gray = gray
            frame_num += 1
        except Exception as e:
            log(f"[Error] Frame {frame_num}: {e}", True)
            frame_num += 1
            continue

    cap.release()
    end_time = time.time()

    print_summary(frame_num, saved_frame_num, start_time, end_time)


def run_from_config(main_config_path: str):
    try:
        main_config = load_main_config(main_config_path)
        step_config_path = main_config["steps"].get(STEP_NAME)
        config = load_step_config(step_config_path, main_config_path)

        output_folder = config["output"].get("folder") or f"data/frame/{STEP_NAME}_{TIMESTAMP}"
        ensure_directory_exists(output_folder)

        extract_unique_frames(
            video_path=config["video"]["path"],
            output_folder=output_folder,
            diff_threshold=config["settings"]["diff_threshold"],
            save_first_frame=config["settings"].get("save_first_frame", True),
            verbose=config["settings"].get("verbose", True),
            log_skipped_frames=config["settings"].get("log_skipped_frames", False),
            save_gray_diff_map=config["settings"].get("save_gray_diff_map", False)
        )
    except Exception as e:
        log(f"[Fatal Error] {e}", True)
        sys.exit(1)


if __name__ == "__main__":
    run_from_config(MAIN_CONFIG_PATH)
