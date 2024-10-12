let isFileUploaded = false;

async function uploadPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    const messageArea = document.getElementById('uploadMessage');
    const querySection = document.getElementById('querySection');

    if (!file) {
        alert('Please select a file');
        return;
    }

    messageArea.textContent = "File is uploading...";
    messageArea.style.color = "blue";

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:8000/upload_pdf/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        document.getElementById('result').innerText = JSON.stringify(result, null, 2);
        
        messageArea.textContent = "File uploaded successfully!";
        messageArea.style.color = "green";
        
        // Enable query section
        isFileUploaded = true;
        enableQuerySection();
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'Error uploading file: ' + error.message;
        
        messageArea.textContent = "Error uploading file.";
        messageArea.style.color = "red";
        
        // Ensure query section is disabled
        isFileUploaded = false;
        disableQuerySection();
    }
}

function enableQuerySection() {
    const queryInput = document.getElementById('queryInput');
    const submitButton = document.querySelector('.query-section button');
    queryInput.disabled = false;
    submitButton.disabled = false;
}

function disableQuerySection() {
    const queryInput = document.getElementById('queryInput');
    const submitButton = document.querySelector('.query-section button');
    queryInput.disabled = true;
    submitButton.disabled = true;
}

async function submitQuery() {
    if (!isFileUploaded) {
        alert('Please upload a file before submitting a query.');
        return;
    }

    const query = document.getElementById('queryInput').value;
    if (!query) {
        alert('Please enter a query');
        return;
    }


    try {
        const response = await fetch('http://localhost:8000/query/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: query })
        });

        const result = await response.json();
        document.getElementById('result').innerText = JSON.stringify(result, null, 2);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'Error submitting query: ' + error.message;
    }
}




// Initially disable the query section
disableQuerySection();