# Enhanced PDF Reader with AI Analysis

A modern web-based PDF reader with advanced AI-powered features for text analysis, summarization, and exam question generation.

## 🚀 Features

### Core PDF Reading
- **PDF Upload & Viewing**: Drag-and-drop PDF upload with page-by-page navigation
- **Text Extraction**: Extract text from PDF documents with easy copy/save functionality
- **Audio Reading**: Text-to-speech with adjustable speed and volume controls
- **Zoom Controls**: Zoom in/out for better readability
- **Responsive Design**: Modern, mobile-friendly interface

### AI-Powered Analysis
- **PDF Summarization**: Generate concise summaries of PDF content using AI
- **Key Points Extraction**: Automatically identify and extract key points from documents
- **Document Statistics**: Word count, sentence count, readability scores, and grade level analysis
- **Exam Question Generation**: Create multiple choice and theory questions from PDF content
- **Question Export**: Export questions in JSON, TXT, or HTML formats

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd PythoncordingChallege
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and go to `http://localhost:8080`

## 📋 Requirements

### Python Dependencies
- **Flask**: Web framework
- **PyMuPDF**: PDF processing
- **Pillow**: Image processing
- **pyttsx3**: Text-to-speech
- **transformers**: AI models for summarization and question generation
- **torch**: PyTorch for AI model support
- **nltk**: Natural language processing
- **spacy**: Advanced NLP
- **textstat**: Text statistics and readability analysis

### Optional AI Enhancement
For enhanced AI capabilities, you can set an OpenAI API key:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## 🎯 How to Use

### Basic PDF Reading
1. **Upload PDF**: Drag and drop a PDF file or click to browse
2. **Navigate**: Use arrow buttons or keyboard shortcuts (←/→)
3. **Extract Text**: Click "Extract Text" to get text content
4. **Audio Reading**: Use the audio controls to read text aloud
5. **Save Text**: Download extracted text as a file

### AI Analysis Features
1. **Generate Summary**: 
   - Extract text from PDF first
   - Click "Summarize" button
   - View summary, key points, and statistics in the Summary tab

2. **Generate Questions**:
   - Extract text from PDF first
   - Go to Questions tab
   - Select question types (Multiple Choice/Theory)
   - Set number of questions
   - Click "Generate Questions"
   - View generated questions with answers and explanations

3. **Export Questions**:
   - Generate questions first
   - Click "Export Questions" button
   - Choose format (JSON, TXT, HTML)
   - Download the file

## 🔧 Technical Details

### AI Models Used
- **Summarization**: Facebook BART-large-CNN model
- **Question Generation**: Google Flan-T5 model
- **Text Analysis**: NLTK and spaCy for natural language processing

### Architecture
- **Backend**: Flask web server with AI model integration
- **Frontend**: Modern HTML5/CSS3/JavaScript with responsive design
- **AI Processing**: Local AI models with fallback to rule-based methods

### File Structure
```
PythoncordingChallege/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── app.js        # Frontend JavaScript
└── templates/
    └── index.html        # Main HTML template
```

## 🎨 Features in Detail

### PDF Summarization
- **AI-Powered**: Uses state-of-the-art transformer models
- **Fallback**: Rule-based summarization when AI models unavailable
- **Key Points**: Automatically extracts important concepts
- **Statistics**: Provides document analysis metrics

### Question Generation
- **Multiple Choice**: Generate questions with 4 options and correct answers
- **Theory Questions**: Create open-ended questions with expected answers
- **Smart Analysis**: Uses content analysis to create relevant questions
- **Export Options**: Multiple formats for different use cases

### Audio Features
- **Text-to-Speech**: Browser-based speech synthesis
- **Speed Control**: Adjustable reading speed
- **Volume Control**: Adjustable audio volume
- **Progress Tracking**: Visual progress indicator

## 🚀 Future Enhancements

- [ ] **Advanced AI Models**: Integration with GPT-4 and other advanced models
- [ ] **Question Difficulty**: Automatic difficulty assessment
- [ ] **Study Mode**: Interactive quiz mode with scoring
- [ ] **Batch Processing**: Process multiple PDFs simultaneously
- [ ] **Cloud Storage**: Save and sync documents across devices
- [ ] **Collaboration**: Share summaries and questions with others

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PyMuPDF**: For excellent PDF processing capabilities
- **Transformers**: For providing state-of-the-art AI models
- **Flask**: For the robust web framework
- **Font Awesome**: For beautiful icons

---

**Enjoy reading PDFs with AI-powered analysis! 📚✨** 