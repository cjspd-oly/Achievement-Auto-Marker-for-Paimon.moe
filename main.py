import os
import toml

# === Constants ===
MAIN_CONFIG_PATH = "config/main_config.toml"
DEFAULT_CONFIG_PATHS = {
    "frame_extraction": "config/frame_extraction.toml",
    "ocr_extraction": "config/ocr_extraction.toml",
    "import_generator": "config/import_generator.toml",
}


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_main_config_if_not_exists():
    """Create main_config.toml if it does not exist, with default step config paths."""
    ensure_directory(os.path.dirname(MAIN_CONFIG_PATH))
    if not os.path.exists(MAIN_CONFIG_PATH):
        default_main_config = {"steps": DEFAULT_CONFIG_PATHS}
        with open(MAIN_CONFIG_PATH, "w") as f:
            toml.dump(default_main_config, f)
        print(f"[Init] Created default main config at: {MAIN_CONFIG_PATH}")
    else:
        print(f"[Info] Main config found at: {MAIN_CONFIG_PATH}")


# === ENTRY POINT ===
if __name__ == "__main__":
    create_main_config_if_not_exists()

    # STEP 1: Frame Extraction
    from pipeline.frame_extractor import run_from_config as frame_extraction

    frame_extraction(MAIN_CONFIG_PATH)
    print("\n\n\n")

    # STEP 2: OCR Extraction
    from pipeline.ocr_extractor import run_from_config as ocr_extraction

    ocr_extraction(MAIN_CONFIG_PATH)
    print("\n\n\n")

    # STEP 3: Import Generation
    from pipeline.import_generator import run_from_config as import_generation

    import_generation(MAIN_CONFIG_PATH)
    print("\n\n\n")

    # TODO: [Testing] Comparator
    # from comparator import run_from_config as comparation
    # comparation(MAIN_CONFIG_PATH)
