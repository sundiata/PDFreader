# PDF Reader with Audio Application

A modern, feature-rich PDF reader built with Python and Tkinter that includes **text-to-speech functionality**. This application provides a user-friendly interface for viewing PDFs, extracting text, and **reading PDFs aloud**.

## Features

- **PDF Viewing**: Display PDF pages with zoom and scroll capabilities
- **Text Extraction**: Extract text from PDF documents
- **🎵 Audio Reading**: Read PDF text aloud with text-to-speech
- **Audio Controls**: Play, pause, and stop audio reading
- **Voice Settings**: Adjust reading speed and volume
- **Navigation**: Easy page-by-page navigation
- **Zoom Controls**: Zoom in/out and reset zoom level
- **Text Viewer**: Separate tab for viewing extracted text
- **Save Functionality**: Save extracted text to files
- **Modern UI**: Clean, intuitive interface with proper styling

## Installation

1. **Clone or download the project files**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install PyPDF2==3.0.1 PyMuPDF==1.23.8 Pillow==10.1.0 pyttsx3==2.90 playsound==1.3.0
   ```

## Usage

1. **Run the application**:
   ```bash
   python index.py
   ```

2. **Open a PDF**:
   - Click the "Open PDF" button
   - Select a PDF file from your computer
   - The PDF will load and display the first page

3. **Navigate through pages**:
   - Use the "◀" and "▶" buttons to move between pages
   - The current page number is displayed in the navigation area

4. **Zoom controls**:
   - Click "Zoom +" to zoom in
   - Click "Zoom -" to zoom out
   - Click "Reset" to return to original size

5. **Extract text**:
   - Click "Extract Text" to extract all text from the PDF
   - Switch to the "Text Viewer" tab to see the extracted text
   - Use "Save Text" to save the extracted text to a file

6. **🎵 Audio Reading**:
   - After extracting text, click "🔊 Play" to start reading aloud
   - Use "⏹ Stop" to stop reading
   - Use "⏸ Pause" to pause/resume reading
   - Adjust reading speed (50-250 words per minute)
   - Adjust volume (0.1-1.0)
   - Monitor reading progress in the progress bar

## File Structure

```
PDFcordingChallenge/
├── index.py          # Main application file with audio features
├── requirements.txt  # Python dependencies including TTS
└── README.md        # This file
```

## Requirements

- Python 3.7 or higher
- Tkinter (usually comes with Python)
- PyMuPDF (fitz) for PDF processing
- PyPDF2 for additional PDF functionality
- Pillow for image processing
- **pyttsx3 for text-to-speech functionality**
- **playsound for audio playback**

## Audio Features

### Text-to-Speech Engine
- Uses **pyttsx3** for cross-platform text-to-speech
- Supports multiple voices (system-dependent)
- Adjustable speech rate and volume
- Sentence-by-sentence reading for better control

### Audio Controls
- **Play**: Start reading the extracted text aloud
- **Stop**: Immediately stop audio reading
- **Pause**: Pause and resume reading
- **Speed Control**: Adjust reading speed from 50 to 250 WPM
- **Volume Control**: Adjust audio volume from 0.1 to 1.0

### Reading Progress
- Real-time progress indicator
- Shows current sentence being read
- Displays total reading progress

## Troubleshooting

### Common Issues

1. **Import Error for fitz**:
   - Make sure PyMuPDF is installed: `pip install PyMuPDF`

2. **TTS initialization error**:
   - On macOS: TTS should work out of the box
   - On Windows: May need to install additional speech engines
   - On Linux: Install espeak: `sudo apt-get install espeak`

3. **Tkinter not found**:
   - On Ubuntu/Debian: `sudo apt-get install python3-tk`
   - On macOS: Tkinter should be included with Python
   - On Windows: Tkinter should be included with Python

4. **PDF won't load**:
   - Ensure the PDF file is not corrupted
   - Check if the file path contains special characters
   - Make sure you have read permissions for the file

5. **Audio not working**:
   - Check system audio settings
   - Ensure speakers/headphones are connected
   - Try different voice settings

### Performance Tips

- Large PDF files may take longer to load
- Zoom operations on large files may be slower
- Text extraction from very large documents may take some time
- Audio reading works best with clean, well-formatted text

## Features in Detail

### PDF Viewer Tab
- Displays PDF pages as images
- Supports horizontal and vertical scrolling
- Maintains aspect ratio during zoom operations
- Smooth page transitions

### Text Viewer Tab
- Shows extracted text with proper formatting
- Supports word wrap for better readability
- Scrollable text area for long documents
- Page separators for easy navigation

### Audio Controls Panel
- Dedicated audio control buttons with icons
- Real-time voice settings adjustment
- Progress tracking during reading
- Status updates for audio operations

### File Operations
- Open PDF files with file dialog
- Extract text from entire document
- Save extracted text to text files
- Support for various file formats

## Accessibility Features

This PDF reader is designed with accessibility in mind:
- **Screen Reader Compatible**: Works with system screen readers
- **Keyboard Navigation**: All features accessible via keyboard
- **High Contrast**: Clear visual indicators for audio controls
- **Audio Feedback**: Text-to-speech for all extracted content

## Contributing

Feel free to enhance this PDF reader with additional features such as:
- Multiple voice selection
- Audio file export
- Bookmark support
- Search functionality
- Multiple document tabs
- Print functionality
- Annotation tools
- OCR for scanned PDFs

## License

This project is open source and available under the MIT License. 