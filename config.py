import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ================== CORE SETTINGS ==================
# Input/Output directories - use absolute paths
INPUT_DIR = os.path.abspath(os.getenv("INPUT_DIR", "./media"))
OUTPUT_DIR = os.path.abspath(os.getenv("OUTPUT_DIR", "./transcripts"))

# Whisper model configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# ================== VALIDATION ==================
# Create directories if they don't exist
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Validate Whisper model
VALID_MODELS = ["tiny", "base", "small", "medium", "large"]
if WHISPER_MODEL not in VALID_MODELS:
    raise ValueError(
        f"Invalid WHISPER_MODEL: {WHISPER_MODEL}. "
        f"Valid options: {VALID_MODELS}"
    )

# ================== LOGGING ==================
# Ensure log directory exists
log_file = Path(__file__).parent / "transcription.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# ================== DEBUG INFO ==================
logging.info(f"Configuration loaded successfully")
logging.info(f"Input directory: {Path(INPUT_DIR).resolve()}")
logging.info(f"Output directory: {Path(OUTPUT_DIR).resolve()}")
logging.info(f"Using Whisper model: {WHISPER_MODEL}")