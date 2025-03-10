import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import config
import os
import sys
from pathlib import Path
import traceback
import time
from processor import Transcriber

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Transcription Suite")
        
        # Add system info to help with debugging
        self.log_system_info()
        
        # Initialize transcriber in a separate thread
        self.transcriber = None
        self.loading_model = True
        self.setup_style()
        self.create_widgets()
        self.setup_layout()
        
        # Start transcriber initialization
        threading.Thread(target=self.init_transcriber).start()

    def log_system_info(self):
        """Log system information for debugging"""
        import platform
        import pkg_resources
        
        info = [
            f"System: {platform.system()} {platform.release()} ({platform.version()})",
            f"Python: {sys.version}",
            f"Working directory: {os.getcwd()}",
            "Installed packages:"
        ]
        
        packages = sorted(['torch', 'whisper', 'librosa', 'numpy', 'soundfile', 'resampy'])
        for pkg in packages:
            try:
                version = pkg_resources.get_distribution(pkg).version
                info.append(f"  - {pkg}: {version}")
            except pkg_resources.DistributionNotFound:
                info.append(f"  - {pkg}: Not installed")
        
        # Check if FFmpeg is installed
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            info.append(f"FFmpeg: Available ({result.stdout.split('\\n')[0]})")
        except (subprocess.SubprocessError, FileNotFoundError):
            info.append("FFmpeg: Not found in PATH")
            
        for line in info:
            print(line)

    def init_transcriber(self):
        """Initialize the transcriber in a background thread"""
        try:
            self.update_status("Loading Whisper model... (this may take a moment)")
            start_time = time.time()
            self.transcriber = Transcriber()
            elapsed = time.time() - start_time
            self.loading_model = False
            self.update_status(f"Ready to transcribe (model loaded in {elapsed:.1f}s)", 'success')
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
        except Exception as e:
            self.update_status(f"Error loading model: {str(e)}", 'error')
            self.root.after(0, lambda: messagebox.showerror("Initialization Error", 
                              f"Failed to initialize Whisper model: {str(e)}\n\n"
                              f"Please check if you have all dependencies installed."))

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Color palette
        self.colors = {
            'primary': '#2A2F3D',    # Dark blue
            'secondary': '#3D434F',   # Medium blue
            'accent': '#00C1B3',     # Teal
            'text': '#FFFFFF',        # White
            'highlight': '#FFA500',   # Orange
            'success': '#4CAF50',     # Green
            'error': '#F44336'        # Red
        }

        # Configure styles
        self.style.configure('TFrame', background=self.colors['primary'])
        self.style.configure('TLabel', 
                           background=self.colors['primary'],
                           foreground=self.colors['text'],
                           font=('Helvetica', 10))
        
        self.style.configure('TButton', 
                           background=self.colors['accent'],
                           foreground=self.colors['text'],
                           font=('Helvetica', 10, 'bold'),
                           borderwidth=1)
        
        self.style.map('TButton',
                     background=[('active', self.colors['highlight'])])

    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self.header = ttk.Frame(self.main_frame)
        ttk.Label(self.header, 
                text="📝 Whisper Transcription", 
                font=('Helvetica', 16, 'bold')).pack(pady=10)
        self.header.pack(fill=tk.X)

        # File selection section
        self.file_frame = ttk.LabelFrame(self.main_frame, text=" File Management ")
        self.create_file_widgets()
        self.file_frame.pack(fill=tk.X, pady=10)

        # Progress section
        self.progress_frame = ttk.Frame(self.main_frame)
        self.create_progress_widgets()
        self.progress_frame.pack(fill=tk.X, pady=10)

        # Output section
        self.output_frame = ttk.LabelFrame(self.main_frame, text=" Transcription Results ")
        self.create_output_widgets()
        self.output_frame.pack(fill=tk.BOTH, expand=True)

        # Debug button
        self.debug_btn = ttk.Button(
            self.main_frame,
            text="🔍 Debug Selected File",
            command=self.debug_selected_file
        )
        self.debug_btn.pack(fill=tk.X, pady=5)

        # Status bar
        self.status_bar = ttk.Label(self.main_frame, 
                                  relief=tk.SUNKEN,
                                  anchor=tk.W,
                                  font=('Helvetica', 9))
        self.status_bar.pack(fill=tk.X, pady=(10,0))
        
        # Initially show loading status
        self.update_status("Loading Whisper model...", 'info')

    def create_file_widgets(self):
        # File list frame with scrollbar
        list_frame = ttk.Frame(self.file_frame)
        
        self.file_list = tk.Listbox(list_frame, 
                                  bg=self.colors['secondary'],
                                  fg=self.colors['text'],
                                  selectbackground=self.colors['accent'],
                                  font=('Helvetica', 10))
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scrollbar.set)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button panel
        btn_panel = ttk.Frame(self.file_frame)
        ttk.Button(btn_panel, 
                 text="➕ Add Files", 
                 command=self.add_files).pack(fill=tk.X, pady=2)
        ttk.Button(btn_panel, 
                 text="🗑️ Remove Selected", 
                 command=self.remove_selected).pack(fill=tk.X, pady=2)
        ttk.Button(btn_panel, 
                 text="🗑️ Clear All", 
                 command=self.clear_queue).pack(fill=tk.X, pady=2)
        btn_panel.pack(side=tk.RIGHT, padx=5)

    def create_progress_widgets(self):
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          orient=tk.HORIZONTAL,
                                          mode='determinate')
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        self.start_btn = ttk.Button(self.progress_frame, 
                                  text="▶️ Start Transcription",
                                  command=self.start_processing,
                                  state=tk.DISABLED)  # Initially disabled until model loads
        self.start_btn.pack(side=tk.RIGHT, padx=5)

    def create_output_widgets(self):
        self.output_text = scrolledtext.ScrolledText(self.output_frame,
                                                   bg=self.colors['secondary'],
                                                   fg=self.colors['text'],
                                                   insertbackground=self.colors['text'],
                                                   font=('Consolas', 10),
                                                   wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_layout(self):
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.configure(bg=self.colors['primary'])

    def add_files(self):
        file_types = [("Audio Files", "*.mp3 *.wav *.m4a *.ogg *.flac")]
        files = filedialog.askopenfilenames(filetypes=file_types)
        
        valid_files = []
        for f in files:
            # Validate each file exists
            if os.path.exists(f):
                self.file_list.insert(tk.END, f)
                valid_files.append(f)
            else:
                self.output_text.insert(tk.END, f"❌ Error: File not found: {f}\n")
                
        self.update_status(f"Added {len(valid_files)} files to queue")

    def remove_selected(self):
        """Remove selected file from the list"""
        selection = self.file_list.curselection()
        if selection:
            self.file_list.delete(selection[0])
            self.update_status("Removed selected file from queue")

    def debug_selected_file(self):
        """Run debug process on selected file"""
        selection = self.file_list.curselection()
        if not selection:
            messagebox.showinfo("Debug", "Please select a file to debug first")
            return
            
        file_path = self.file_list.get(selection[0])
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.output_text.insert(tk.END, f"❌ Debug Error: File does not exist: {file_path}\n")
            return
            
        # Show file info
        file_info = Path(file_path)
        self.output_text.insert(tk.END, f"\n==== DEBUG INFO ====\n")
        self.output_text.insert(tk.END, f"File: {file_info.name}\n")
        self.output_text.insert(tk.END, f"Absolute path: {file_info.resolve()}\n")
        self.output_text.insert(tk.END, f"Size: {file_info.stat().st_size} bytes\n")
        self.output_text.insert(tk.END, f"Exists: {file_info.exists()}\n")
        
        # Disable button during debug
        self.debug_btn.config(state=tk.DISABLED)
        self.update_status(f"Debugging file: {file_info.name}...")
        
        # Run debug in thread
        threading.Thread(target=self.run_debug_process, args=(file_path,)).start()

    def run_debug_process(self, file_path):
        """Run debug process in a separate thread"""
        try:
            if not self.transcriber:
                self.output_text.insert(tk.END, "Transcriber not initialized yet.\n")
                return
                
            # Try to transcribe small portion first
            self.output_text.insert(tk.END, "Starting debug transcription...\n")
            
            # Try direct transcription
            start_time = time.time()
            output_path = self.transcriber.transcribe_file(file_path)
            elapsed = time.time() - start_time
            
            self.output_text.insert(tk.END, f"✅ Debug transcription complete in {elapsed:.1f}s!\n")
            self.output_text.insert(tk.END, f"Output saved to: {output_path}\n")
            
            # Try to read the output
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.output_text.insert(tk.END, "--- Transcription Preview ---\n")
                    preview = content[:200] + "..." if len(content) > 200 else content
                    self.output_text.insert(tk.END, preview + "\n")
            except Exception as read_error:
                self.output_text.insert(tk.END, f"⚠️ Warning: Could not read result file: {str(read_error)}\n")
            
            self.update_status(f"Debug complete - transcription successful!", 'success')
            
        except Exception as e:
            error_details = traceback.format_exc()
            self.output_text.insert(tk.END, f"❌ Debug Error: {str(e)}\n")
            self.output_text.insert(tk.END, f"Details: {error_details}\n")
            self.update_status(f"Debug failed - see error details", 'error')
        finally:
            self.root.after(0, lambda: self.debug_btn.config(state=tk.NORMAL))

    def clear_queue(self):
        self.file_list.delete(0, tk.END)
        self.update_status("Queue cleared", 'success')

    def update_status(self, message, category='info'):
        color_map = {
            'info': self.colors['text'],
            'success': self.colors['success'],
            'error': self.colors['error']
        }
        # Update in a thread-safe way
        self.root.after(0, lambda: self.status_bar.config(text=message, foreground=color_map[category]))

    def start_processing(self):
        if self.loading_model:
            messagebox.showinfo("Processing", "Please wait for the model to finish loading.")
            return
            
        if not self.file_list.size():
            self.update_status("Error: No files in queue!", 'error')
            return

        self.progress_bar.config(maximum=self.file_list.size())
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.process_files).start()

    def process_files(self):
        for idx in range(self.file_list.size()):
            file_path = self.file_list.get(0)
            try:
                self.update_status(f"Processing: {file_path}")
                self.output_text.insert(tk.END, f"{'='*40}\n")
                self.output_text.insert(tk.END, f"File: {file_path}\n")
                self.output_text.insert(tk.END, f"{'-'*40}\n")
                
                start_time = time.time()
                output_path = self.transcriber.transcribe_file(file_path)
                elapsed = time.time() - start_time
                
                self.output_text.insert(tk.END, f"Completed in {elapsed:.1f} seconds\n")
                
                try:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        self.output_text.insert(tk.END, f.read() + "\n\n")
                except Exception as read_error:
                    self.output_text.insert(tk.END, f"⚠️ Warning: Could not read result file: {str(read_error)}\n\n")
                
                self.file_list.delete(0)
                self.progress_bar['value'] += 1
                
            except Exception as e:
                error_details = traceback.format_exc()
                self.output_text.insert(tk.END, f"❌ Error processing {file_path}: {str(e)}\n")
                self.output_text.insert(tk.END, f"Details: {error_details}\n\n")
            finally:
                self.root.update_idletasks()
        
        self.update_status("Processing complete!", 'success')
        self.start_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()