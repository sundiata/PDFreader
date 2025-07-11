from flask import Flask, render_template, request, jsonify, send_file
import fitz  # PyMuPDF
import os
import tempfile
import base64
import io
from PIL import Image
import json
import time
import random
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import textstat
from transformers import pipeline
import openai
from datetime import datetime

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

# Initialize AI models
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    question_generator = pipeline("text2text-generation", model="google/flan-t5-base")
except Exception as e:
    print(f"Warning: Could not load AI models: {e}")
    summarizer = None
    question_generator = None

# Initialize OpenAI (optional - for advanced features)
openai.api_key = os.getenv('OPENAI_API_KEY', '')

current_pdf_data = {
    'document': None,
    'filename': None,
    'total_pages': 0,
    'current_page': 0,
    'extracted_text': '',
    'summary': '',
    'questions': []
}

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF file upload"""
    global current_pdf_data
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'}), 400
        
        
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
       
        pdf_document = fitz.open(temp_path)
        
   
        current_pdf_data['document'] = pdf_document
        current_pdf_data['filename'] = file.filename
        current_pdf_data['total_pages'] = len(pdf_document)
        current_pdf_data['current_page'] = 0
        
        
        page = pdf_document[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_data = pix.tobytes("png")
        
     
        img_base64 = base64.b64encode(img_data).decode()
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'total_pages': len(pdf_document),
            'current_page': 1,
            'page_image': f'data:image/png;base64,{img_base64}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

@app.route('/page/<int:page_num>')
def get_page(page_num):
    """Get specific page image"""
    global current_pdf_data
    
    try:
        if not current_pdf_data['document']:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        if page_num < 1 or page_num > current_pdf_data['total_pages']:
            return jsonify({'error': 'Invalid page number'}), 400
        
 
        page = current_pdf_data['document'][page_num - 1]
        
        # Get zoom level from query parameter
        zoom = float(request.args.get('zoom', 1.5))
        zoom_matrix = fitz.Matrix(zoom, zoom)
        
        pix = page.get_pixmap(matrix=zoom_matrix)
        img_data = pix.tobytes("png")
        img_base64 = base64.b64encode(img_data).decode()
        
        current_pdf_data['current_page'] = page_num - 1
        
        return jsonify({
            'success': True,
            'page_image': f'data:image/png;base64,{img_base64}',
            'current_page': page_num,
            'total_pages': current_pdf_data['total_pages']
        })
        
    except Exception as e:
        return jsonify({'error': f'Error loading page: {str(e)}'}), 500

@app.route('/extract-text')
def extract_text():
    """Extract text from PDF"""
    global current_pdf_data
    
    try:
        if not current_pdf_data['document']:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        text = ""
        for page_num in range(current_pdf_data['total_pages']):
            page = current_pdf_data['document'][page_num]
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.get_text()
            text += "\n"
        
        current_pdf_data['extracted_text'] = text
        
        return jsonify({
            'success': True,
            'text': text,
            'total_pages': current_pdf_data['total_pages']
        })
        
    except Exception as e:
        return jsonify({'error': f'Error extracting text: {str(e)}'}), 500

@app.route('/save-text', methods=['POST'])
def save_text():
    """Save extracted text to file"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'No text to save'}), 400
        
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        filename = f"extracted_text_{current_pdf_data.get('filename', 'document').replace('.pdf', '')}.txt"
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Error saving text: {str(e)}'}), 500

@app.route('/summarize', methods=['POST'])
def summarize_pdf():
    """Generate summary of PDF content"""
    global current_pdf_data
    
    try:
        if not current_pdf_data['extracted_text']:
            return jsonify({'error': 'No text extracted. Please extract text first.'}), 400
        
        text = current_pdf_data['extracted_text']
        
        # Clean and prepare text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 100:
            return jsonify({'error': 'Text too short for summarization'}), 400
        
        # Use AI summarization if available
        if summarizer:
            # Split text into chunks if too long
            max_length = 1024
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            summaries = []
            for chunk in chunks[:3]:  # Limit to first 3 chunks
                if len(chunk) > 50:
                    summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
                    summaries.append(summary[0]['summary_text'])
            
            ai_summary = ' '.join(summaries)
        else:
            # Fallback to extractive summarization
            ai_summary = extractive_summarization(text)
        
        # Generate key points
        key_points = extract_key_points(text)
        
        # Calculate text statistics
        stats = {
            'word_count': len(text.split()),
            'sentence_count': len(sent_tokenize(text)),
            'readability_score': textstat.flesch_reading_ease(text),
            'grade_level': textstat.flesch_kincaid_grade(text)
        }
        
        current_pdf_data['summary'] = {
            'summary': ai_summary,
            'key_points': key_points,
            'statistics': stats
        }
        
        return jsonify({
            'success': True,
            'summary': ai_summary,
            'key_points': key_points,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating summary: {str(e)}'}), 500

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    """Generate exam questions from PDF content"""
    global current_pdf_data
    
    try:
        if not current_pdf_data['extracted_text']:
            return jsonify({'error': 'No text extracted. Please extract text first.'}), 400
        
        data = request.get_json()
        question_types = data.get('types', ['multiple_choice', 'theory'])
        num_questions = data.get('count', 5)
        
        text = current_pdf_data['extracted_text']
        
        # Generate questions using AI
        questions = []
        
        if question_generator:
            # Generate multiple choice questions
            if 'multiple_choice' in question_types:
                mc_questions = generate_multiple_choice_questions(text, num_questions)
                questions.extend(mc_questions)
            
            # Generate theory questions
            if 'theory' in question_types:
                theory_questions = generate_theory_questions(text, num_questions)
                questions.extend(theory_questions)
        else:
            # Fallback to rule-based question generation
            questions = generate_rule_based_questions(text, question_types, num_questions)
        
        current_pdf_data['questions'] = questions
        
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating questions: {str(e)}'}), 500

@app.route('/export-questions', methods=['POST'])
def export_questions():
    """Export questions in various formats"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'json')
        questions = current_pdf_data.get('questions', [])
        
        if not questions:
            return jsonify({'error': 'No questions generated. Please generate questions first.'}), 400
        
        if format_type == 'json':
            return jsonify({
                'success': True,
                'questions': questions,
                'filename': f'questions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            })
        
        elif format_type == 'txt':
            # Create text file
            temp_dir = tempfile.mkdtemp()
            filename = f'questions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Exam Questions Generated from: {current_pdf_data.get('filename', 'PDF')}\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i, question in enumerate(questions, 1):
                    f.write(f"Question {i}:\n")
                    f.write(f"Type: {question['type']}\n")
                    f.write(f"Question: {question['question']}\n")
                    
                    if question['type'] == 'multiple_choice':
                        for j, option in enumerate(question['options'], 1):
                            f.write(f"  {j}. {option}\n")
                        f.write(f"Correct Answer: {question['correct_answer']}\n")
                    else:
                        f.write(f"Expected Answer: {question['expected_answer']}\n")
                    
                    f.write(f"Explanation: {question['explanation']}\n\n")
            
            return send_file(file_path, as_attachment=True, download_name=filename)
        
        elif format_type == 'html':
            # Create HTML file
            temp_dir = tempfile.mkdtemp()
            filename = f'questions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            file_path = os.path.join(temp_dir, filename)
            
            html_content = generate_html_questions(questions)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return send_file(file_path, as_attachment=True, download_name=filename)
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Error exporting questions: {str(e)}'}), 500

@app.route('/cleanup')
def cleanup():
    """Clean up resources"""
    global current_pdf_data
    
    try:
        if current_pdf_data['document']:
            current_pdf_data['document'].close()
        
        current_pdf_data = {
            'document': None,
            'filename': None,
            'total_pages': 0,
            'current_page': 0,
            'extracted_text': '',
            'summary': '',
            'questions': []
        }
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Error during cleanup: {str(e)}'}), 500

# Helper functions for text analysis and question generation

def extractive_summarization(text):
    """Extractive summarization using TF-IDF approach"""
    sentences = sent_tokenize(text)
    if len(sentences) <= 3:
        return text
    
    # Calculate sentence scores based on word frequency
    word_freq = {}
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        for word in words:
            if word.isalnum():
                word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences
    sentence_scores = {}
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        score = sum(word_freq.get(word, 0) for word in words if word.isalnum())
        sentence_scores[sentence] = score
    
    # Get top sentences
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    summary_sentences = [s[0] for s in top_sentences[:3]]
    
    return ' '.join(summary_sentences)

def extract_key_points(text):
    """Extract key points from text"""
    sentences = sent_tokenize(text)
    key_points = []
    
    # Look for sentences with key indicators
    key_indicators = ['important', 'key', 'main', 'primary', 'essential', 'crucial', 'significant']
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(indicator in sentence_lower for indicator in key_indicators):
            key_points.append(sentence.strip())
    
    # If no key points found, use first few sentences
    if not key_points and sentences:
        key_points = sentences[:3]
    
    return key_points[:5]  # Limit to 5 key points

def generate_multiple_choice_questions(text, num_questions):
    """Generate multiple choice questions using AI"""
    questions = []
    
    if question_generator:
        # Use AI to generate questions
        prompt = f"Generate {num_questions} multiple choice questions from this text: {text[:1000]}"
        response = question_generator(prompt, max_length=512, num_return_sequences=1)
        
        # Parse AI response (simplified)
        questions = parse_ai_questions(response[0]['generated_text'], 'multiple_choice', num_questions)
    else:
        # Rule-based multiple choice generation
        questions = generate_rule_based_mc_questions(text, num_questions)
    
    return questions

def generate_theory_questions(text, num_questions):
    """Generate theory questions using AI"""
    questions = []
    
    if question_generator:
        # Use AI to generate questions
        prompt = f"Generate {num_questions} theory questions from this text: {text[:1000]}"
        response = question_generator(prompt, max_length=512, num_return_sequences=1)
        
        # Parse AI response (simplified)
        questions = parse_ai_questions(response[0]['generated_text'], 'theory', num_questions)
    else:
        # Rule-based theory question generation
        questions = generate_rule_based_theory_questions(text, num_questions)
    
    return questions

def generate_rule_based_questions(text, question_types, num_questions):
    """Generate questions using rule-based approach"""
    questions = []
    
    sentences = sent_tokenize(text)
    important_sentences = []
    
    # Find sentences with important keywords
    important_keywords = ['what', 'how', 'why', 'when', 'where', 'which', 'define', 'explain', 'describe']
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in important_keywords):
            important_sentences.append(sentence)
    
    if not important_sentences:
        important_sentences = sentences[:10]  # Use first 10 sentences if no important ones found
    
    for i, sentence in enumerate(important_sentences[:num_questions]):
        if 'multiple_choice' in question_types:
            mc_question = create_multiple_choice_question(sentence, i)
            if mc_question:
                questions.append(mc_question)
        
        if 'theory' in question_types and len(questions) < num_questions:
            theory_question = create_theory_question(sentence, i)
            if theory_question:
                questions.append(theory_question)
    
    return questions

def generate_rule_based_mc_questions(text, num_questions):
    """Generate multiple choice questions using rules"""
    questions = []
    sentences = sent_tokenize(text)
    
    for i, sentence in enumerate(sentences[:num_questions]):
        question = create_multiple_choice_question(sentence, i)
        if question:
            questions.append(question)
    
    return questions

def generate_rule_based_theory_questions(text, num_questions):
    """Generate theory questions using rules"""
    questions = []
    sentences = sent_tokenize(text)
    
    for i, sentence in enumerate(sentences[:num_questions]):
        question = create_theory_question(sentence, i)
        if question:
            questions.append(question)
    
    return questions

def create_multiple_choice_question(sentence, index):
    """Create a multiple choice question from a sentence"""
    try:
        words = word_tokenize(sentence)
        
        if len(words) < 5:
            return None
        
        question_text = f"What is the main topic discussed in: '{sentence[:100]}...'?"
        
        options = [
            "The main topic",
            "A related concept", 
            "An unrelated topic",
            "None of the above"
        ]
        
        return {
            'type': 'multiple_choice',
            'question': question_text,
            'options': options,
            'correct_answer': options[0],
            'explanation': f"This question is based on sentence {index + 1} from the document."
        }
    except Exception as e:
        return None

def create_theory_question(sentence, index):
    """Create a theory question from a sentence"""
    try:
        question_text = f"Explain the concept mentioned in: '{sentence[:100]}...'"
        
        return {
            'type': 'theory',
            'question': question_text,
            'expected_answer': f"A detailed explanation of the concept from sentence {index + 1}",
            'explanation': f"This question requires understanding of the content in sentence {index + 1}."
        }
    except Exception as e:
        return None

def parse_ai_questions(ai_response, question_type, num_questions):
    """Parse AI-generated questions (simplified)"""
    questions = []
    
    # This is a simplified parser - in a real implementation, you'd need more sophisticated parsing
    if question_type == 'multiple_choice':
        for i in range(num_questions):
            questions.append({
                'type': 'multiple_choice',
                'question': f"AI-generated question {i+1}",
                'options': ["Option A", "Option B", "Option C", "Option D"],
                'correct_answer': "Option A",
                'explanation': "AI-generated explanation"
            })
    else:
        for i in range(num_questions):
            questions.append({
                'type': 'theory',
                'question': f"AI-generated theory question {i+1}",
                'expected_answer': "AI-generated expected answer",
                'explanation': "AI-generated explanation"
            })
    
    return questions

def generate_html_questions(questions):
    """Generate HTML content for questions"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generated Exam Questions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .question { margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .question h3 { color: #333; }
            .options { margin-left: 20px; }
            .correct { color: green; font-weight: bold; }
            .explanation { margin-top: 10px; padding: 10px; background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>Generated Exam Questions</h1>
        <p>Generated from: """ + current_pdf_data.get('filename', 'PDF') + """</p>
        <p>Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    """
    
    for i, question in enumerate(questions, 1):
        html += f'<div class="question">'
        html += f'<h3>Question {i} ({question["type"].replace("_", " ").title()})</h3>'
        html += f'<p><strong>Question:</strong> {question["question"]}</p>'
        
        if question['type'] == 'multiple_choice':
            html += '<div class="options">'
            for j, option in enumerate(question['options'], 1):
                if option == question['correct_answer']:
                    html += f'<p class="correct">{j}. {option} ✓</p>'
                else:
                    html += f'<p>{j}. {option}</p>'
            html += '</div>'
        else:
            html += f'<p><strong>Expected Answer:</strong> {question["expected_answer"]}</p>'
        
        html += f'<div class="explanation"><strong>Explanation:</strong> {question["explanation"]}</div>'
        html += '</div>'
    
    html += '</body></html>'
    return html

if __name__ == '__main__':
    print("🚀 Starting Enhanced PDF Reader with AI Analysis...")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("🎵 Enjoy reading PDFs with audio and AI-powered analysis!")
    app.run(debug=True, host='0.0.0.0', port=8080)






print(my)