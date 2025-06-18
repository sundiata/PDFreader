from flask import Flask, render_template, request, jsonify, send_file
import fitz  # PyMuPDF
import os
import tempfile
import base64
import io
from PIL import Image
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables to store current PDF data
current_pdf_data = {
    'document': None,
    'filename': None,
    'total_pages': 0,
    'current_page': 0,
    'extracted_text': ''
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
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(temp_path)
        
        # Store PDF data
        current_pdf_data['document'] = pdf_document
        current_pdf_data['filename'] = file.filename
        current_pdf_data['total_pages'] = len(pdf_document)
        current_pdf_data['current_page'] = 0
        
        # Get first page image
        page = pdf_document[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_data = pix.tobytes("png")
        
        # Convert to base64 for web display
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
        
        # Get page (convert to 0-based index)
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
            'extracted_text': ''
        }
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Error during cleanup: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting PDF Reader with Audio Web Application...")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("🎵 Enjoy reading PDFs with audio!")
    app.run(debug=True, host='0.0.0.0', port=8080) 