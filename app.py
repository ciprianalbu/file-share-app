
from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string
import os
import random
import string
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mapping codes to filename and upload info
file_store = {}

EXPIRATION_OPTIONS = {
    '1h': 60 * 60,
    '12h': 12 * 60 * 60,
    '24h': 24 * 60 * 60,
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Share App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">

<h1 class="mb-4">File Share</h1>

<div class="row">
    <div class="col-md-6">
        <h3>Upload a File</h3>
        <form method="POST" enctype="multipart/form-data">
            <div class="mb-3">
                <input type="file" name="file" class="form-control" required>
            </div>
            <div class="mb-3">
                <label>Expire after:</label>
                <select name="expire" class="form-select">
                    <option value="1h">1 hour</option>
                    <option value="12h">12 hours</option>
                    <option value="24h" selected>24 hours</option>
                </select>
            </div>
            <input type="submit" value="Upload" class="btn btn-primary">
        </form>
        {% if code %}
        <div class="alert alert-success mt-3">
            <strong>Your code:</strong> <span id="code">{{ code }}</span>
            <button onclick="copyCode()" class="btn btn-sm btn-secondary">Copy</button>
            <p>Share this code with someone so they can download your file.</p>
        </div>
        {% endif %}
    </div>

    <div class="col-md-6">
        <h3>Download a File</h3>
        <form method="POST" action="/download">
            <div class="mb-3">
                <input type="text" name="code" class="form-control" placeholder="Enter code" required>
            </div>
            <input type="submit" value="Download" class="btn btn-success">
        </form>
        {% if error %}
        <div class="alert alert-danger mt-3">{{ error }}</div>
        {% endif %}
    </div>
</div>

<script>
function copyCode() {
    var code = document.getElementById("code").innerText;
    navigator.clipboard.writeText(code);
    alert("Code copied to clipboard: " + code);
}
</script>

</body>
</html>
"""

def cleanup_expired():
    now = time.time()
    expired = [code for code, data in file_store.items() if now - data['timestamp'] > data['expire_seconds']]
    
    for code in expired:
        filepath = os.path.join(UPLOAD_FOLDER, file_store[code]['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        del file_store[code]

@app.route("/", methods=["GET", "POST"])
def upload():
    code = None
    if request.method == "POST":
        file = request.files["file"]
        expire_choice = request.form.get("expire", "24h")
        expire_seconds = EXPIRATION_OPTIONS.get(expire_choice, EXPIRATION_OPTIONS["24h"])
        
        if file:
            cleanup_expired()
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            filename = code + "_" + file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            file_store[code] = {
                'filename': filename,
                'timestamp': time.time(),
                'expire_seconds': expire_seconds
            }
    return render_template_string(HTML_TEMPLATE, code=code)

@app.route("/download", methods=["GET", "POST"])
def download():
    error = None
    if request.method == "POST":
        cleanup_expired()
        code = request.form["code"].strip()
        data = file_store.get(code)
        if data:
            filepath = os.path.join(UPLOAD_FOLDER, data['filename'])
            if os.path.exists(filepath):
                os.remove(filepath)
                del file_store[code]
                return send_from_directory(UPLOAD_FOLDER, data['filename'], as_attachment=True)
            else:
                del file_store[code]
                error = "File no longer available."
        else:
            error = "Invalid or expired code!"
    return render_template_string(HTML_TEMPLATE, error=error)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
