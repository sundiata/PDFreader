# PDF Reader with Audio - Web Application

A modern, responsive web-based PDF reader built with **HTML, CSS, and JavaScript** that includes **text-to-speech functionality**. This application provides a beautiful, user-friendly interface for viewing PDFs, extracting text, and **reading PDFs aloud** in any modern web browser.

## 🌟 Features

- **📄 PDF Viewing**: Display PDF pages with zoom and scroll capabilities
- **📝 Text Extraction**: Extract text from PDF documents
- **🎵 Audio Reading**: Read PDF text aloud with browser text-to-speech
- **🎛️ Audio Controls**: Play, pause, and stop audio reading
- **⚙️ Voice Settings**: Adjust reading speed and volume
- **🧭 Navigation**: Easy page-by-page navigation with keyboard shortcuts
- **🔍 Zoom Controls**: Zoom in/out and reset zoom level
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **💾 Save Functionality**: Save extracted text to files
- **🎨 Modern UI**: Beautiful, intuitive interface with animations

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web application**:
   ```bash
   python app.py
   ```

3. **Open your browser** and go to:
   ```
   http://localhost:8080
   ```

## 📁 File Structure

```
PDFcordingChallenge/
├── app.py                 # Flask web server
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Modern CSS styles
│   └── js/
│       └── app.js        # JavaScript functionality
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🎯 How to Use

### **1. Upload PDF**
- **Drag & Drop**: Simply drag your PDF file onto the upload area
- **Click to Browse**: Click the upload area to select a file
- **Supported**: All standard PDF files

### **2. Navigate & View**
- **Page Navigation**: Use ◀ ▶ buttons or arrow keys
- **Zoom Controls**: Use + - buttons or keyboard shortcuts
- **Keyboard Shortcuts**:
  - `←` `→` - Previous/Next page
  - `+` `-` - Zoom in/out
  - `0` - Reset zoom
  - `Space` - Pause/Resume reading
  - `Escape` - Stop reading

### **3. Extract Text**
- Click "Extract Text" to extract all text from the PDF
- Switch to "Text Viewer" tab to see the extracted text
- Use "Save Text" to download the text as a file

### **4. 🎵 Audio Reading**
- After extracting text, click "🔊 Play" to start reading aloud
- Use "⏹ Stop" to stop reading
- Use "⏸ Pause" to pause/resume reading
- Adjust reading speed (Slow to Very Fast)
- Adjust volume (0-100%)
- Monitor reading progress in real-time

## 🛠️ Technical Stack

### **Frontend**
- **HTML5**: Semantic markup and modern structure
- **CSS3**: Advanced styling with gradients, animations, and responsive design
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Font Awesome**: Beautiful icons
- **Google Fonts**: Inter font family for modern typography

### **Backend**
- **Flask**: Lightweight Python web framework
- **PyMuPDF**: High-performance PDF processing
- **Pillow**: Image processing for PDF rendering

### **Audio Features**
- **Web Speech API**: Native browser text-to-speech
- **Cross-browser Support**: Works in Chrome, Firefox, Safari, Edge
- **Real-time Controls**: Adjust speed and volume on the fly

## 🎨 Design Features

### **Modern UI/UX**
- **Glassmorphism**: Beautiful frosted glass effects
- **Gradient Backgrounds**: Eye-catching color schemes
- **Smooth Animations**: Hover effects and transitions
- **Responsive Grid**: Adapts to any screen size
- **Dark/Light Elements**: Balanced contrast and readability

### **Interactive Elements**
- **Drag & Drop**: Intuitive file upload
- **Real-time Feedback**: Loading states and progress indicators
- **Toast Notifications**: Success, error, and warning messages
- **Tabbed Interface**: Organized content sections

## 📱 Responsive Design

The application is fully responsive and works perfectly on:
- **Desktop**: Full-featured experience with all controls
- **Tablet**: Optimized layout with touch-friendly buttons
- **Mobile**: Streamlined interface for small screens

## 🔧 Requirements

- **Python 3.7+**
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **Internet Connection** (for fonts and icons)

### **Python Dependencies**
- Flask==2.3.3
- PyMuPDF==1.23.8
- PyPDF2==3.0.1
- Pillow==10.1.0

## 🚀 Advanced Features

### **Browser Text-to-Speech**
- **Native Support**: Uses browser's built-in speech synthesis
- **Multiple Voices**: System-dependent voice selection
- **Speed Control**: Adjustable reading speed
- **Volume Control**: Adjustable audio volume
- **Progress Tracking**: Real-time reading progress

### **PDF Processing**
- **High Performance**: Fast PDF loading and rendering
- **Zoom Support**: Dynamic zoom with image quality preservation
- **Text Extraction**: Accurate text extraction from all PDF types
- **File Management**: Automatic cleanup and resource management

### **User Experience**
- **Keyboard Shortcuts**: Full keyboard navigation
- **Drag & Drop**: Intuitive file upload
- **Progress Indicators**: Visual feedback for all operations
- **Error Handling**: Graceful error messages and recovery

## 🐛 Troubleshooting

### **Common Issues**

1. **PDF won't upload**:
   - Ensure file is a valid PDF
   - Check file size (max 16MB)
   - Try refreshing the page

2. **Audio not working**:
   - Check browser permissions for audio
   - Ensure speakers/headphones are connected
   - Try a different browser (Chrome recommended)

3. **Page not loading**:
   - Check if Flask server is running
   - Verify port 8080 is available
   - Check browser console for errors

4. **Text extraction fails**:
   - Ensure PDF contains extractable text
   - Try a different PDF file
   - Check server logs for errors

5. **Port 5000 conflict (macOS)**:
   - The app now uses port 8080 to avoid conflicts with AirPlay Receiver
   - If you need to use a different port, modify `app.py` line 184

### **Browser Compatibility**
- **Chrome**: Full support, recommended
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Internet Explorer**: Not supported

## 🔮 Future Enhancements

Potential features for future versions:
- **Multiple Voice Selection**: Choose from available system voices
- **Audio File Export**: Save audio as MP3/WAV files
- **Bookmark Support**: Save and manage page bookmarks
- **Search Functionality**: Search within PDF content
- **Multiple Document Tabs**: Open multiple PDFs simultaneously
- **Print Functionality**: Print PDF pages directly
- **Annotation Tools**: Add notes and highlights
- **OCR Support**: Extract text from scanned PDFs
- **Cloud Storage**: Upload to Google Drive, Dropbox, etc.

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

---

**Enjoy reading your PDFs with audio! 🎵📚** 