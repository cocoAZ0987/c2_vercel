from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import os
from vercel_kv import kv

app = Flask(__name__)
CORS(app)

@app.route('/api/result', methods=['POST'])
def receive_result():
    """Reçoit le résultat d'une commande exécutée"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        output = data.get('output', '')
        command = data.get('command', '')
        
        if not agent_id:
            return jsonify({'error': 'agent_id required'}), 400
        
        key = f"agent:{agent_id}"
        existing = kv.get(key)
        
        if not existing:
            return jsonify({'error': 'Agent not found'}), 404
        
        agent_data = json.loads(existing)
        
        # Ajouter le résultat
        if 'results' not in agent_data:
            agent_data['results'] = []
        
        agent_data['results'].append({
            'command': command,
            'output': output[:5000],  # Limiter la taille
            'time': datetime.datetime.now().isoformat()
        })
        
        # Garder seulement les 50 derniers résultats
        if len(agent_data['results']) > 50:
            agent_data['results'] = agent_data['results'][-50:]
        
        # Sauvegarder
        kv.set(key, json.dumps(agent_data))
        
        return jsonify({'status': 'received'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)