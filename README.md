# Whisper Transcription Tool

A desktop application that leverages OpenAI's Whisper model to transcribe audio files into text. This GUI-based application, built with Python's Tkinter library, provides an easy-to-use interface for converting various audio formats (e.g., MP3, WAV, M4A) into readable text transcripts.

## Features

- **Audio Transcription:** Uses the Whisper model to accurately transcribe audio files.
- **Graphical User Interface (GUI):** User-friendly interface for adding, managing, and processing audio files.
- **Real-Time Progress Tracking:** Displays transcription progress with a status bar and progress indicator.
- **Debug Mode:** Provides detailed file information and troubleshooting output for selected files.
- **Configurable Settings:** Customize input/output directories and model selection through the `.env` file.
- **Comprehensive Logging:** Detailed logs are saved for auditing and troubleshooting purposes.

## Project Structure

```
├── .env                 # Environment variables (e.g., Whisper model, output directory)
├── config.py            # Application configuration (directories, model validation, logging)
├── gui.py               # Tkinter-based GUI implementation
├── main.py              # Entry point to launch the application
├── processor.py         # Contains the Transcriber class wrapping the Whisper transcription
├── requirements.txt     # List of required Python dependencies
└── transcription.log    # Log file recording transcription events and errors
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/techsavvymohan/WhisperTranscriptionTool
   cd WhisperTranscriptionTool
   ```

2. **Set Up a Virtual Environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Edit the `.env` file to adjust settings if necessary. The default configuration is:

   ```
   WHISPER_MODEL=base
   OUTPUT_DIR=./transcripts
   ```

## Usage

1. **Launch the Application:**

   Run the main entry point:

   ```bash
   python main.py
   ```

2. **Using the GUI:**
   - **Add Files:** Click the "Add Files" button to select audio files for transcription.
   - **Remove/Clear Files:** Use the provided buttons to remove individual files or clear the entire queue.
   - **Start Transcription:** Click "Start Transcription" to begin processing the queued files.
   - **Debug Mode:** Use the "Debug Selected File" button to retrieve detailed file information and troubleshoot issues.
   - **View Output:** Monitor the progress bar and check the transcription results in the output text area.

## Troubleshooting

- **FFmpeg Requirement:** Ensure FFmpeg is installed and available in your system's PATH since it is necessary for audio processing.
- **Dependency Issues:** Verify all dependencies listed in `requirements.txt` are installed.
- **Log Files:** Check `transcription.log` for detailed error messages and processing logs if issues arise.

## Acknowledgements

- Built with OpenAI's Whisper model for robust audio transcription.
- GUI implemented using Python's Tkinter library.
- Designed to provide a simple yet powerful transcription solution for diverse audio inputs.
