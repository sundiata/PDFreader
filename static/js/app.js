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
            a.download = `extracted_text_${Date.now()}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showNotification('Text saved successfully!', 'success');
        } else {
            const data = await response.json();
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error saving text', 'error');
        console.error('Save error:', error);
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
        document.querySelector('.tab-btn:first-child').classList.add('active');
        document.getElementById('viewerTab').classList.add('active');
    } else if (tabName === 'text') {
        document.querySelector('.tab-btn:last-child').classList.add('active');
        document.getElementById('textTab').classList.add('active');
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
