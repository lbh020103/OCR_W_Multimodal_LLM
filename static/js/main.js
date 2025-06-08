// JavaScript for OCR web application

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadForm = document.getElementById('uploadForm');
    const urlForm = document.getElementById('urlForm');
    const fileUpload = document.getElementById('fileUpload');
    const outputFormat = document.getElementById('outputFormat');
    const urlOutputFormat = document.getElementById('urlOutputFormat');
    const imageUrl = document.getElementById('imageUrl');
    const resultText = document.getElementById('resultText');
    const imagePreview = document.getElementById('imagePreview');
    const imagePreviewContainer = document.querySelector('.image-preview-container');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const copyBtn = document.getElementById('copyBtn');
    
    // Handle file upload form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate file input
        if (!fileUpload.files || fileUpload.files.length === 0) {
            showMessage('Please select an image file to upload', 'error');
            return;
        }
        
        const file = fileUpload.files[0];
        
        // Check if file is an image
        if (!file.type.startsWith('image/')) {
            showMessage('Please select a valid image file', 'error');
            return;
        }
        
        // Show loading indicator
        showLoading(true);
        
        // Display image preview
        displayImagePreview(file);
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('output_format', outputFormat.value);
        
        try {
            // Send request to server
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            handleResponse(response);
        } catch (error) {
            showLoading(false);
            showMessage(`Error: ${error.message}`, 'error');
        }
    });
    
    // Handle URL form submission
    urlForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate URL input
        const url = imageUrl.value.trim();
        if (!url) {
            showMessage('Please enter an image URL', 'error');
            return;
        }
        
        // Show loading indicator
        showLoading(true);
        
        // Display image preview from URL
        displayImagePreviewFromUrl(url);
        
        try {
            // Send request to server
            const response = await fetch('/ocr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_url: url,
                    output_format: urlOutputFormat.value
                })
            });
            
            handleResponse(response);
        } catch (error) {
            showLoading(false);
            showMessage(`Error: ${error.message}`, 'error');
        }
    });
    
    // Copy button functionality
    copyBtn.addEventListener('click', function() {
        const text = resultText.textContent;
        navigator.clipboard.writeText(text)
            .then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    });
    
    // Handle the response from the server
    async function handleResponse(response) {
        showLoading(false);
        
        if (!response.ok) {
            let errorMessage = `Server error: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {}
            
            showMessage(errorMessage, 'error');
            return;
        }
        
        const data = await response.json();
        
        if (data.response_message) {
            resultText.textContent = data.response_message;
            formatResultIfJSON(data.response_message);
            copyBtn.disabled = false;
        } else {
            showMessage('No results returned from the server', 'error');
        }
    }
    
    // Display image preview for uploaded file
    function displayImagePreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreviewContainer.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
    }
    
    // Display image preview from URL
    function displayImagePreviewFromUrl(url) {
        imagePreview.src = url;
        imagePreview.onerror = function() {
            imagePreviewContainer.classList.add('d-none');
            showMessage('Could not load image preview', 'warning');
        };
        imagePreview.onload = function() {
            imagePreviewContainer.classList.remove('d-none');
        };
    }
    
    // Show/hide loading indicator
    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.classList.remove('d-none');
            resultText.textContent = '';
            copyBtn.disabled = true;
        } else {
            loadingIndicator.classList.add('d-none');
        }
    }
    
    // Show message in the result area
    function showMessage(message, type = 'info') {
        resultText.textContent = message;
        copyBtn.disabled = true;
        
        // Could add classes based on message type (error, warning, info)
        if (type === 'error') {
            resultText.style.color = '#dc3545';
        } else if (type === 'warning') {
            resultText.style.color = '#ffc107';
        } else {
            resultText.style.color = '';
        }
        
        // Reset color after 5 seconds
        setTimeout(() => {
            resultText.style.color = '';
        }, 5000);
    }
    
    // Try to format JSON result for better display
    function formatResultIfJSON(text) {
        try {
            // Check if the text is valid JSON
            const jsonObj = JSON.parse(text);
            const formattedJson = JSON.stringify(jsonObj, null, 2);
            resultText.textContent = formattedJson;
        } catch (e) {
            // Not valid JSON, leave as is
        }
    }
}); 