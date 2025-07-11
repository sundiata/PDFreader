console.log('PDF Reader App loaded');

// Global variables
let currentPage = 1;
let totalPages = 1;
let currentZoom = 1.5;
let extractedText = '';
let isReading = false;
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;

// DOM elements
const uploadSection = document.getElementById('uploadSection');
const viewerSection = document.getElementById('viewerSection');
const uploadArea = document.getElementById('uploadArea');
const pdfFile = document.getElementById('pdfFile');
const pageImage = document.getElementById('pageImage');
const pageInfo = document.getElementById('pageInfo');
const textViewer = document.getElementById('textViewer');
const statusText = document.getElementById('statusText');
const loadingOverlay = document.getElementById('loadingOverlay');
const notificationContainer = document.getElementById('notificationContainer');
const readingProgress = document.getElementById('readingProgress');
const progressText = document.getElementById('progressText');
const progressFill = document.getElementById('progressFill');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateStatus('Ready - No PDF loaded');
    console.log('🎵 PDF Reader with Audio loaded successfully!');
});

function initializeEventListeners() {
    // File upload events
    pdfFile.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Click to upload
    uploadArea.addEventListener('click', () => pdfFile.click());
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// File handling functions
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadPDF(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            uploadPDF(file);
        } else {
            showNotification('Please upload a PDF file', 'error');
        }
    }
}

async function uploadPDF(file) {
    showLoading(true);
    updateStatus('Uploading PDF...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPage = data.current_page;
            totalPages = data.total_pages;
            pageImage.src = data.page_image;
            updatePageInfo();
            showViewer();
            updateStatus(`Loaded: ${data.filename} - ${totalPages} pages`);
            showNotification('PDF uploaded successfully!', 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error uploading PDF', 'error');
        console.error('Upload error:', error);
    } finally {
        showLoading(false);
    }
}

// Navigation functions
async function nextPage() {
    if (currentPage < totalPages) {
        await loadPage(currentPage + 1);
    }
}

async function previousPage() {
    if (currentPage > 1) {
        await loadPage(currentPage - 1);
    }
}

async function loadPage(pageNum) {
    showLoading(true);
    updateStatus(`Loading page ${pageNum}...`);
    
    try {
        const response = await fetch(`/page/${pageNum}?zoom=${currentZoom}`);
        const data = await response.json();
        
        if (data.success) {
            currentPage = data.current_page;
            pageImage.src = data.page_image;
            updatePageInfo();
            updateStatus(`Page ${currentPage} of ${totalPages}`);
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error loading page', 'error');
        console.error('Page load error:', error);
    } finally {
        showLoading(false);
    }
}

// Zoom functions
async function zoomIn() {
    currentZoom = Math.min(currentZoom * 1.2, 3.0);
    await loadPage(currentPage);
}

async function zoomOut() {
    currentZoom = Math.max(currentZoom / 1.2, 0.5);
    await loadPage(currentPage);
}

async function resetZoom() {
    currentZoom = 1.5;
    await loadPage(currentPage);
}

// Text extraction functions
async function extractText() {
    showLoading(true);
    updateStatus('Extracting text...');
    
    try {
        const response = await fetch('/extract-text');
        const data = await response.json();
        
        if (data.success) {
            extractedText = data.text;
            textViewer.value = extractedText;
            switchTab('text');
            updateStatus(`Text extracted from ${data.total_pages} pages - Ready for audio reading`);
            showNotification('Text extracted successfully!', 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error extracting text', 'error');
        console.error('Text extraction error:', error);
    } finally {
        showLoading(false);
    }
}

async function saveText() {
    if (!extractedText.trim()) {
        showNotification('No text to save. Please extract text first.', 'warning');
        return;
    }

    showLoading(true);
    updateStatus('Saving text...');
    
    try {
        const response = await fetch('/save-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: extractedText })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'extracted_text.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            updateStatus('Text saved successfully');
            showNotification('Text file downloaded!', 'success');
        } else {
            const data = await response.json();
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error saving text', 'error');
        console.error('Save error:', error);
    } finally {
        showLoading(false);
    }
}

// AI Analysis functions
async function summarizePDF() {
    if (!extractedText.trim()) {
        showNotification('No text extracted. Please extract text first.', 'warning');
        return;
    }

    showLoading(true);
    updateStatus('Generating summary...');
    
    try {
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySummary(data);
            switchTab('summary');
            updateStatus('Summary generated successfully');
            showNotification('PDF summarized successfully!', 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error generating summary', 'error');
        console.error('Summary error:', error);
    } finally {
        showLoading(false);
    }
}

function displaySummary(data) {
    const summaryContent = document.getElementById('summaryContent');
    const keyPointsContent = document.getElementById('keyPointsContent');
    const statsContent = document.getElementById('statsContent');
    
    // Display summary
    summaryContent.innerHTML = `<p>${data.summary}</p>`;
    
    // Display key points
    if (data.key_points && data.key_points.length > 0) {
        const keyPointsList = data.key_points.map(point => `<li>${point}</li>`).join('');
        keyPointsContent.innerHTML = `<ul>${keyPointsList}</ul>`;
    } else {
        keyPointsContent.innerHTML = '<p class="placeholder">No key points identified</p>';
    }
    
    // Display statistics
    if (data.statistics) {
        const stats = data.statistics;
        statsContent.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${stats.word_count}</div>
                <div class="stat-label">Words</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.sentence_count}</div>
                <div class="stat-label">Sentences</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${Math.round(stats.readability_score)}</div>
                <div class="stat-label">Readability Score</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${Math.round(stats.grade_level)}</div>
                <div class="stat-label">Grade Level</div>
            </div>
        `;
    } else {
        statsContent.innerHTML = '<p class="placeholder">Statistics not available</p>';
    }
}

async function generateQuestions() {
    if (!extractedText.trim()) {
        showNotification('No text extracted. Please extract text first.', 'warning');
        return;
    }

    const mcQuestions = document.getElementById('mcQuestions').checked;
    const theoryQuestions = document.getElementById('theoryQuestions').checked;
    const questionCount = parseInt(document.getElementById('questionCount').value);

    if (!mcQuestions && !theoryQuestions) {
        showNotification('Please select at least one question type.', 'warning');
        return;
    }

    showLoading(true);
    updateStatus('Generating questions...');
    
    try {
        const questionTypes = [];
        if (mcQuestions) questionTypes.push('multiple_choice');
        if (theoryQuestions) questionTypes.push('theory');
        
        const response = await fetch('/generate-questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                types: questionTypes,
                count: questionCount
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayQuestions(data.questions);
            switchTab('questions');
            updateStatus(`Generated ${data.total_questions} questions successfully`);
            showNotification(`Generated ${data.total_questions} questions!`, 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error generating questions', 'error');
        console.error('Question generation error:', error);
    } finally {
        showLoading(false);
    }
}

function displayQuestions(questions) {
    const questionsContent = document.getElementById('questionsContent');
    
    if (!questions || questions.length === 0) {
        questionsContent.innerHTML = '<p class="placeholder">No questions generated</p>';
        return;
    }
    
    const questionsHTML = questions.map((question, index) => {
        let questionHTML = `
            <div class="question-item">
                <div class="question-header">
                    <span class="question-type">${question.type.replace('_', ' ').toUpperCase()}</span>
                </div>
                <div class="question-text">${question.question}</div>
        `;
        
        if (question.type === 'multiple_choice') {
            questionHTML += '<div class="question-options">';
            question.options.forEach((option, optionIndex) => {
                const isCorrect = option === question.correct_answer;
                questionHTML += `<div class="question-option ${isCorrect ? 'correct' : ''}">${optionIndex + 1}. ${option}</div>`;
            });
            questionHTML += '</div>';
        } else {
            questionHTML += `<div class="question-answer"><strong>Expected Answer:</strong> ${question.expected_answer}</div>`;
        }
        
        questionHTML += `<div class="question-explanation"><strong>Explanation:</strong> ${question.explanation}</div>`;
        questionHTML += '</div>';
        
        return questionHTML;
    }).join('');
    
    questionsContent.innerHTML = questionsHTML;
}

async function exportQuestions() {
    const questionsContent = document.getElementById('questionsContent');
    
    if (questionsContent.querySelector('.placeholder')) {
        showNotification('No questions to export. Please generate questions first.', 'warning');
        return;
    }

    showLoading(true);
    updateStatus('Exporting questions...');
    
    try {
        // Get export format from user
        const format = prompt('Enter export format (json, txt, html):', 'txt');
        
        if (!format || !['json', 'txt', 'html'].includes(format)) {
            showNotification('Invalid format. Please use: json, txt, or html', 'error');
            return;
        }
        
        const response = await fetch('/export-questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ format: format })
        });
        
        if (response.ok) {
            if (format === 'json') {
                const data = await response.json();
                const blob = new Blob([JSON.stringify(data.questions, null, 2)], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = data.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `questions.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }
            
            updateStatus('Questions exported successfully');
            showNotification(`Questions exported as ${format.toUpperCase()} file!`, 'success');
        } else {
            const data = await response.json();
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error exporting questions', 'error');
        console.error('Export error:', error);
    } finally {
        showLoading(false);
    }
}

// Text-to-speech functions
function startReading() {
    if (!extractedText.trim()) {
        showNotification('No text to read. Please extract text first.', 'warning');
        return;
    }
    
    if (isReading) {
        return;
    }
    
    if (!speechSynthesis) {
        showNotification('Text-to-speech not supported in this browser', 'error');
        return;
    }
    
    isReading = true;
    updateReadingProgress(true);
    updateStatus('Reading text aloud...');
    
    // Clean text for better speech
    const cleanText = cleanTextForSpeech(extractedText);
    const sentences = cleanText.split('. ');
    
    let currentSentenceIndex = 0;
    
    function speakNextSentence() {
        if (!isReading || currentSentenceIndex >= sentences.length) {
            finishReading();
            return;
        }
        
        const sentence = sentences[currentSentenceIndex];
        if (sentence.trim()) {
            currentUtterance = new SpeechSynthesisUtterance(sentence + '.');
            currentUtterance.rate = parseFloat(document.getElementById('speedControl').value);
            currentUtterance.volume = parseFloat(document.getElementById('volumeControl').value);
            
            currentUtterance.onend = () => {
                currentSentenceIndex++;
                updateProgress(currentSentenceIndex, sentences.length);
                speakNextSentence();
            };
            
            currentUtterance.onerror = (event) => {
                console.error('Speech error:', event);
                finishReading();
            };
            
            speechSynthesis.speak(currentUtterance);
        } else {
            currentSentenceIndex++;
            speakNextSentence();
        }
    }
    
    speakNextSentence();
}

function stopReading() {
    isReading = false;
    if (speechSynthesis) {
        speechSynthesis.cancel();
    }
    if (currentUtterance) {
        currentUtterance = null;
    }
    updateReadingProgress(false);
    updateStatus('Reading stopped');
}

function pauseReading() {
    if (isReading) {
        if (speechSynthesis.speaking) {
            speechSynthesis.pause();
            updateStatus('Reading paused');
        } else if (speechSynthesis.paused) {
            speechSynthesis.resume();
            updateStatus('Reading resumed');
        }
    } else {
        startReading();
    }
}

function finishReading() {
    isReading = false;
    currentUtterance = null;
    updateReadingProgress(false);
    updateStatus('Reading completed');
    showNotification('Text reading completed', 'success');
}

function updateVoiceSettings() {
    if (currentUtterance) {
        currentUtterance.rate = parseFloat(document.getElementById('speedControl').value);
        currentUtterance.volume = parseFloat(document.getElementById('volumeControl').value);
    }
}

function cleanTextForSpeech(text) {
    // Remove extra whitespace and newlines
    text = text.replace(/\s+/g, ' ');
    
    // Remove special characters that might interfere with speech
    text = text.replace(/[^\w\s\.\,\!\?\-]/g, '');
    
    return text.trim();
}

// UI helper functions
function showViewer() {
    uploadSection.style.display = 'none';
    viewerSection.style.display = 'block';
}

function updatePageInfo() {
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    if (tabName === 'viewer') {
        document.querySelector('.tab-btn:nth-child(1)').classList.add('active');
        document.getElementById('viewerTab').classList.add('active');
    } else if (tabName === 'text') {
        document.querySelector('.tab-btn:nth-child(2)').classList.add('active');
        document.getElementById('textTab').classList.add('active');
    } else if (tabName === 'summary') {
        document.querySelector('.tab-btn:nth-child(3)').classList.add('active');
        document.getElementById('summaryTab').classList.add('active');
    } else if (tabName === 'questions') {
        document.querySelector('.tab-btn:nth-child(4)').classList.add('active');
        document.getElementById('questionsTab').classList.add('active');
    }
}

function updateStatus(message) {
    statusText.textContent = message;
}

function updateReadingProgress(show) {
    readingProgress.style.display = show ? 'flex' : 'none';
}

function updateProgress(current, total) {
    const percentage = (current / total) * 100;
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `Reading... ${current}/${total}`;
}

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Keyboard shortcuts
function handleKeyboardShortcuts(event) {
    // Only handle shortcuts when viewer is visible
    if (viewerSection.style.display === 'none') return;
    
    switch (event.key) {
        case 'ArrowLeft':
            event.preventDefault();
            previousPage();
            break;
        case 'ArrowRight':
            event.preventDefault();
            nextPage();
            break;
        case '+':
        case '=':
            event.preventDefault();
            zoomIn();
            break;
        case '-':
            event.preventDefault();
            zoomOut();
            break;
        case '0':
            event.preventDefault();
            resetZoom();
            break;
        case ' ':
            event.preventDefault();
            pauseReading();
            break;
        case 'Escape':
            event.preventDefault();
            stopReading();
            break;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (isReading) {
        stopReading();
    }
    
    // Cleanup server resources
    fetch('/cleanup').catch(console.error);
});
