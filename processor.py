import whisper
import os
import logging
from pathlib import Path
import config

class Transcriber:
    def __init__(self):
        """Initialize the Whisper model with configuration"""
        try:
            logging.info("Initializing Whisper model...")
            self.model = whisper.load_model(config.WHISPER_MODEL)
            logging.info(f"Loaded Whisper model: {config.WHISPER_MODEL}")
        except Exception as e:
            logging.error(f"Failed to initialize model: {str(e)}")
            raise

    def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe an audio file and save results
        Args:
            file_path: Path to audio file
        Returns:
            Path to saved transcription file
        """
        try:
            # Convert to Path object for safer path handling
            file_path_obj = Path(file_path)
            
            # Validate input file
            if not file_path_obj.exists():
                error_msg = f"File not found: {file_path}"
                logging.error(error_msg)
                raise FileNotFoundError(error_msg)

            logging.info(f"Starting transcription: {file_path}")
            
            # Perform transcription
            result = self.model.transcribe(str(file_path_obj.absolute()))
            
            # Generate output path
            output_file = self._generate_output_path(file_path)
            
            # Save results
            self._save_transcription(result["text"], output_file)
            
            logging.info(f"Transcription saved to: {output_file}")
            return output_file

        except Exception as e:
            error_msg = f"Failed to transcribe {file_path}: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

    def _generate_output_path(self, input_path: str) -> str:
        """Generate output path in the configured directory"""
        input_stem = Path(input_path).stem
        output_dir = Path(config.OUTPUT_DIR)
        return str(output_dir.absolute() / f"{input_stem}.txt")

    def _save_transcription(self, text: str, output_path: str):
        """Save transcribed text to file"""
        try:
            # Make sure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
        except IOError as e:
            error_msg = f"Failed to write to {output_path}: {str(e)}"
            logging.error(error_msg)
            raise