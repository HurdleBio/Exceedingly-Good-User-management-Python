from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
from routes.auth import auth_bp

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 3000))

if not os.path.exists('uploads'):
    os.mkdir('uploads')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

app.register_blueprint(auth_bp, url_prefix='/api')

@app.route('/health', methods=['GET'])
def health():
    from datetime import datetime
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(Exception)
def handle_error(err):
    import traceback
    print(traceback.format_exc())
    return jsonify({
        'error': 'Something went wrong!',
        'details': str(err)
    }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({'error': 'Route not found'}), 404

if __name__ == '__main__':
    print(f'🚀 Server running on port {PORT}')
    print(f'📁 Uploads directory: {os.path.join(os.getcwd(), "uploads")}')
    print(f'🔗 Health check: http://localhost:{PORT}/health')
    print(f'👤 Auth routes: http://localhost:{PORT}/api/users')
    app.run(port=PORT, debug=True)

