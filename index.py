import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF
import PyPDF2
import os
from PIL import Image, ImageTk
import threading
import pyttsx3
import time

class PDFReader:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reader with Audio")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.pdf_document = None
        
        # Audio variables
        self.tts_engine = None
        self.is_reading = False
        self.current_text = ""
        self.reading_thread = None
        self.voice_rate = 150
        self.voice_volume = 0.9
        
        # Initialize TTS engine
        self.init_tts_engine()
        
        # Create GUI
        self.create_widgets()
        self.setup_styles()
        
    def init_tts_engine(self):
        """Initialize the text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Set default voice (usually the first one)
                self.tts_engine.setProperty('voice', voices[0].id)
                
        except Exception as e:
            print(f"TTS initialization error: {e}")
            self.tts_engine = None
        
    def setup_styles(self):
        """Configure modern styling for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
       
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#34495e')
        style.configure('Custom.TButton', font=('Arial', 10, 'bold'))
        style.configure('Audio.TButton', font=('Arial', 10, 'bold'), foreground='#27ae60')
        
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
  
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        

        title_label = ttk.Label(main_frame, text="PDF Reader with Audio", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
      
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
       
        file_frame = ttk.LabelFrame(top_frame, text="File Operations", padding=10)
        file_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_frame, text="Open PDF", command=self.open_pdf, style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Extract Text", command=self.extract_text, style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Save Text", command=self.save_text, style='Custom.TButton').pack(side=tk.LEFT)
      
        audio_frame = ttk.LabelFrame(top_frame, text="Audio Controls", padding=10)
        audio_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
     
        self.play_button = ttk.Button(audio_frame, text="🔊 Play", command=self.start_reading, style='Audio.TButton')
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(audio_frame, text="⏹ Stop", command=self.stop_reading, style='Audio.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(audio_frame, text="⏸ Pause", command=self.pause_reading, style='Audio.TButton')
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
    
        ttk.Label(audio_frame, text="Speed:", style='Info.TLabel').pack(side=tk.LEFT, padx=(10, 5))
        self.speed_var = tk.StringVar(value="150")
        speed_combo = ttk.Combobox(audio_frame, textvariable=self.speed_var, values=["50", "100", "150", "200", "250"], width=5)
        speed_combo.pack(side=tk.LEFT, padx=(0, 10))
        speed_combo.bind('<<ComboboxSelected>>', self.update_voice_settings)
        
        ttk.Label(audio_frame, text="Volume:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.volume_var = tk.StringVar(value="0.9")
        volume_combo = ttk.Combobox(audio_frame, textvariable=self.volume_var, values=["0.1", "0.3", "0.5", "0.7", "0.9", "1.0"], width=5)
        volume_combo.pack(side=tk.LEFT, padx=(0, 5))
        volume_combo.bind('<<ComboboxSelected>>', self.update_voice_settings)
   
        nav_frame = ttk.LabelFrame(top_frame, text="Navigation", padding=10)
        nav_frame.pack(side=tk.RIGHT, fill=tk.X)
        
   
        ttk.Button(nav_frame, text="◀", command=self.prev_page, width=3).pack(side=tk.LEFT, padx=(0, 5))
        self.page_label = ttk.Label(nav_frame, text="Page: 0 / 0", style='Info.TLabel')
        self.page_label.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="▶", command=self.next_page, width=3).pack(side=tk.LEFT, padx=(0, 5))
        
        # Zoom controls
        ttk.Button(nav_frame, text="Zoom +", command=self.zoom_in, width=8).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(nav_frame, text="Zoom -", command=self.zoom_out, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="Reset", command=self.reset_zoom, width=6).pack(side=tk.LEFT)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # PDF viewer tab
        self.viewer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viewer_frame, text="PDF Viewer")
        
        # Canvas for PDF display
        self.canvas_frame = ttk.Frame(self.viewer_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', highlightthickness=0)
        self.scrollbar_y = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Text viewer tab
        self.text_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.text_frame, text="Text Viewer")
        
        self.text_viewer = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, font=('Arial', 11))
        self.text_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Audio progress frame
        audio_progress_frame = ttk.Frame(main_frame)
        audio_progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(audio_progress_frame, text="Reading Progress:", style='Info.TLabel').pack(side=tk.LEFT)
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = ttk.Label(audio_progress_frame, textvariable=self.progress_var, style='Info.TLabel')
        progress_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - No PDF loaded")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def update_voice_settings(self, event=None):
        """Update voice rate and volume settings"""
        if self.tts_engine:
            try:
                self.voice_rate = int(self.speed_var.get())
                self.voice_volume = float(self.volume_var.get())
                self.tts_engine.setProperty('rate', self.voice_rate)
                self.tts_engine.setProperty('volume', self.voice_volume)
            except ValueError:
                pass
        
    def start_reading(self):
        """Start reading the current text aloud"""
        if not self.tts_engine:
            messagebox.showerror("Error", "Text-to-speech engine not available")
            return
            
        if not self.current_text:
            messagebox.showwarning("Warning", "No text to read. Please extract text from PDF first.")
            return
            
        if self.is_reading:
            return
            
        self.is_reading = True
        self.progress_var.set("Reading...")
        self.status_var.set("Reading text aloud...")
        
        self.reading_thread = threading.Thread(target=self.read_text_thread)
        self.reading_thread.daemon = True
        self.reading_thread.start()
        
    def read_text_thread(self):
        """Thread function for reading text"""
        try:
            clean_text = self.clean_text_for_speech(self.current_text)
            
            sentences = clean_text.split('. ')
            
            for i, sentence in enumerate(sentences):
                if not self.is_reading:
                    break
                    
                if sentence.strip():
                    self.tts_engine.say(sentence + ".")
                    self.tts_engine.runAndWait()
                    
                    
                    progress = f"Reading... {i+1}/{len(sentences)}"
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Reading error: {str(e)}"))
        finally:
            self.root.after(0, self.finish_reading)
            
    def clean_text_for_speech(self, text):
        """Clean text for better speech synthesis"""
        text = ' '.join(text.split())
        
        
        import re
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        return text
        
    def stop_reading(self):
        """Stop reading"""
        self.is_reading = False
        if self.tts_engine:
            self.tts_engine.stop()
        self.progress_var.set("Stopped")
        self.status_var.set("Reading stopped")
        
    def pause_reading(self):
        """Pause/resume reading"""
        if self.is_reading:
            self.stop_reading()
            self.progress_var.set("Paused")
        else:
            self.start_reading()
            
    def finish_reading(self):
        """Called when reading is finished"""
        self.is_reading = False
        self.progress_var.set("Finished")
        self.status_var.set("Reading completed")
        
    def open_pdf(self):
        """Open and load a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.load_pdf(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
    
    def load_pdf(self, file_path):
        """Load PDF file and display first page"""
        try:
            self.pdf_document = fitz.open(file_path)
            self.current_pdf = file_path
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            
            self.status_var.set(f"Loaded: {os.path.basename(file_path)} - {self.total_pages} pages")
            self.update_page_display()
            self.display_current_page()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
    
    def display_current_page(self):
        """Display the current page on the canvas"""
        if not self.pdf_document:
            return
            
        try:
            # Clear canvas
            self.canvas.delete("all")
            
            # Get page
            page = self.pdf_document[self.current_page]
            
            # Calculate zoom
            zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            self.photo = ImageTk.PhotoImage(img)
            
            # Display on canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")
    
    def update_page_display(self):
        """Update page navigation display"""
        self.page_label.config(text=f"Page: {self.current_page + 1} / {self.total_pages}")
    
    def next_page(self):
        """Go to next page"""
        if self.pdf_document and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_display()
            self.display_current_page()
    
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
            self.display_current_page()
    
    def zoom_in(self):
        """Increase zoom level"""
        self.zoom_level = min(self.zoom_level * 1.2, 3.0)
        if self.pdf_document:
            self.display_current_page()
    
    def zoom_out(self):
        """Decrease zoom level"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.3)
        if self.pdf_document:
            self.display_current_page()
    
    def reset_zoom(self):
        """Reset zoom to original size"""
        self.zoom_level = 1.0
        if self.pdf_document:
            self.display_current_page()
    
    def extract_text(self):
        """Extract text from the current PDF"""
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        try:
            text = ""
            for page_num in range(self.total_pages):
                page = self.pdf_document[page_num]
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.get_text()
                text += "\n"
            
            # Store text for audio reading
            self.current_text = text
            
            # Display in text viewer
            self.text_viewer.delete(1.0, tk.END)
            self.text_viewer.insert(1.0, text)
            
            # Switch to text viewer tab
            self.notebook.select(1)
            
            self.status_var.set(f"Text extracted from {self.total_pages} pages - Ready for audio reading")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract text: {str(e)}")
    
    def save_text(self):
        """Save extracted text to file"""
        text = self.text_viewer.get(1.0, tk.END)
        if not text.strip():
            messagebox.showwarning("Warning", "No text to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Text As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("Success", f"Text saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save text: {str(e)}")

def main():
    """Main function to run the PDF reader"""
    root = tk.Tk()
    app = PDFReader(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    import io  # Import here to avoid circular import
    main()



# list = [1,2,3,4,5,6,7,8,9,10]

# for i in list:
#     print(i)

# if i == 5:
#     print("5 is found")
# else:
#     print("5 is not found")




# 