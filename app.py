import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pdf_processor import scan_pdf_qr

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Configure upload settings
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return "Internal Server Error", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'files[]' not in request.files:
            logger.warning("No file part in the request")
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('files[]')
        results = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                try:
                    file.save(filepath)
                    logger.debug(f"Processing file: {filename}")
                    qr_data = scan_pdf_qr(filepath)

                    results.append({
                        'filename': filename,
                        'qr_data': qr_data,
                        'status': 'success'
                    })

                    # Clean up the temporary file
                    os.remove(filepath)
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")
                    results.append({
                        'filename': filename,
                        'error': str(e),
                        'status': 'error'
                    })
            else:
                logger.warning(f"Invalid file type: {file.filename}")
                results.append({
                    'filename': file.filename,
                    'error': 'Invalid file type',
                    'status': 'error'
                })

        return jsonify(results)
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    logger.warning("File too large")
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)