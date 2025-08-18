document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageInput');
    const fileName = document.getElementById('fileName');
    const detectButton = document.getElementById('detectButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const imageContainer = document.getElementById('imageContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsContent = document.getElementById('resultsContent');
    const jsonContainer = document.getElementById('jsonContainer');
    const jsonOutput = document.getElementById('jsonOutput');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    // Get example images
    const exampleImages = document.querySelectorAll('.example-image');
    
    let selectedFile = null;
    let selectedExampleImage = null;
    
    // Handle file selection (existing functionality)
    imageInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            selectedFile = this.files[0];
            selectedExampleImage = null; // Clear example selection
            fileName.textContent = selectedFile.name;
            detectButton.disabled = false;
            
            // Remove selection from example images
            exampleImages.forEach(img => img.classList.remove('selected'));
        } else {
            selectedFile = null;
            fileName.textContent = 'No file selected';
            detectButton.disabled = true;
        }
    });
    
    // Handle example image selection
    exampleImages.forEach(img => {
        img.addEventListener('click', function() {
            selectedExampleImage = this;
            selectedFile = null; // Clear file input
            imageInput.value = ''; // Clear file input value
            
            // Update UI
            fileName.textContent = this.dataset.name || 'Example image selected';
            detectButton.disabled = false;
            
            // Visual feedback
            exampleImages.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
    
    // Handle detection button click
    detectButton.addEventListener('click', function() {
        if (selectedFile) {
            // Handle uploaded file (existing logic)
            processImageDetection(selectedFile);
        } else if (selectedExampleImage) {
            // Handle example image selection
            fetch(selectedExampleImage.src)
                .then(response => response.blob())
                .then(blob => {
                    const filename = selectedExampleImage.dataset.name + '.jpg';
                    const file = new File([blob], filename, { type: blob.type });
                    processImageDetection(file);
                })
                .catch(error => {
                    showError('Failed to load example image: ' + error.message);
                });
        } else {
            showError('Please select an image file or example image first');
        }
    });
    
    // Common detection processing function
    function processImageDetection(imageFile) {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        // Show loading, hide results
        loadingIndicator.classList.remove('hidden');
        imageContainer.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        jsonContainer.classList.add('hidden');
        errorMessage.classList.add('hidden');
        
        // Send request to backend
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('hidden');
            
            if (data.success) {
                // Store results
                localStorage.setItem('detectionResults', JSON.stringify(data));
                
                // Display image with bounding boxes
                drawImageWithBoxes(imageFile, data.results.detections);
                
                // Display results summary
                displayResults(data);
                
                // Display raw JSON
                displayJSON(data);
            } else {
                showError(data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            loadingIndicator.classList.add('hidden');
            showError('Network error: ' + error.message);
        });
    }
    
    function drawImageWithBoxes(imageFile, detections) {
        const canvas = document.getElementById('canvasOverlay');
        const ctx = canvas.getContext('2d');
        
        const img = new Image();
        img.onload = function() {
            // Set canvas size to image size
            canvas.width = img.width;
            canvas.height = img.height;
            
            // Draw the image
            ctx.drawImage(img, 0, 0);
            
            // Draw bounding boxes
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = 3;
            ctx.font = '16px Arial';
            ctx.fillStyle = '#ff0000';
            ctx.textAlign = 'left';
            
            detections.forEach(detection => {
                const bbox = detection.bbox;
                
                // Draw rectangle
                ctx.strokeRect(bbox.x1, bbox.y1, bbox.width, bbox.height);
                
                // Draw label background
                const label = `${detection.class_name} (${(detection.confidence * 100).toFixed(1)}%)`;
                const textWidth = ctx.measureText(label).width;
                ctx.fillStyle = '#ff0000';
                ctx.fillRect(bbox.x1, bbox.y1 - 25, textWidth + 10, 25);
                
                // Draw label text
                ctx.fillStyle = '#ffffff';
                ctx.fillText(label, bbox.x1 + 5, bbox.y1 - 8);
                ctx.fillStyle = '#ff0000';
            });
        };
        
        // Convert file to data URL
        const reader = new FileReader();
        reader.onload = function(e) {
            img.src = e.target.result;
        };
        reader.readAsDataURL(imageFile);
        
        // Show image container
        imageContainer.classList.remove('hidden');
    }
    
    function displayResults(data) {
        resultsContainer.classList.remove('hidden');
        
        // Create summary HTML
        const summaryHTML = `
            <div class="result-summary">
                <h2>📊 Summary</h2>
                <p>File: ${data.filename}</p>
                <p>Objects detected: ${data.results.total_objects}</p>
                <p>Processing time: ${data.results.processing_time_ms} ms</p>
                <p>Model: ${data.results.model_info.model_name}</p>
                <p>Image size: ${data.results.image_info.width} × ${data.results.image_info.height}</p>
            </div>
        `;
        
        // Create detections list HTML
        let detectionsHTML = '<div class="detection-results"><h2>🎯 Detected Objects</h2>';
        
        if (data.results.detections.length === 0) {
            detectionsHTML += '<p>No objects detected in the image.</p>';
        } else {
            data.results.detections.forEach((detection, index) => {
                detectionsHTML += `
                    <div class="detection-item">
                        <h3>${index + 1}. ${detection.class_name} (${(detection.confidence * 100).toFixed(2)}% confidence)</h3>
                        <p>Position: (${detection.bbox.x1}, ${detection.bbox.y1}) to (${detection.bbox.x2}, ${detection.bbox.y2})</p>
                        <p>Size: ${detection.bbox.width} × ${detection.bbox.height} pixels</p>
                        <p>Center: (${detection.bbox.center_x}, ${detection.bbox.center_y})</p>
                    </div>
                `;
            });
        }
        
        detectionsHTML += '</div>';
        
        // Set content
        resultsContent.innerHTML = summaryHTML + detectionsHTML;
    }
    
    function displayJSON(data) {
        jsonOutput.textContent = JSON.stringify(data, null, 2);
        jsonContainer.classList.remove('hidden');
    }
    
    function showError(message) {
        errorMessage.classList.remove('hidden');
        errorText.textContent = message;
    }
});