from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from vercel_kv import kv

app = Flask(__name__)
CORS(app)

@app.route('/api/command', methods=['POST'])
def send_command():
    """Envoie une commande à un agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        command = data.get('command')
        
        if not agent_id or not command:
            return jsonify({'error': 'agent_id and command required'}), 400
        
        key = f"agent:{agent_id}"
        existing = kv.get(key)
        
        if not existing:
            return jsonify({'error': 'Agent not found'}), 404
        
        agent_data = json.loads(existing)
        
        # Ajouter la commande
        if 'commands' not in agent_data:
            agent_data['commands'] = []
        
        agent_data['commands'].append(command)
        
        # Sauvegarder
        kv.set(key, json.dumps(agent_data))
        
        return jsonify({'status': 'queued', 'command': command})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_results():
    """Efface l'historique des résultats d'un agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'agent_id required'}), 400
        
        key = f"agent:{agent_id}"
        existing = kv.get(key)
        
        if not existing:
            return jsonify({'error': 'Agent not found'}), 404
        
        agent_data = json.loads(existing)
        agent_data['results'] = []
        
        kv.set(key, json.dumps(agent_data))
        
        return jsonify({'status': 'cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)