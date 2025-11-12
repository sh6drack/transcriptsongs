import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from shazam_simple import SimpleShazam

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 1GB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Allowed audio extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: MP3, WAV, M4A, FLAC, AAC, OGG'}), 400

    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Get sampling interval (default 45 seconds for Shazam)
    interval = int(request.form.get('interval', 45))

    try:
        # Analyze with Shazam
        identifier = SimpleShazam()
        songs = identifier.analyze_dj_set(filepath, interval=interval)

        # Format output
        tracklist = identifier.format_tracklist(songs)

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'tracklist': tracklist,
            'songs': songs
        })

    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("🎵 TranscriptSongs (Powered by Shazam)")
    print("Open http://localhost:5001 in your browser\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
