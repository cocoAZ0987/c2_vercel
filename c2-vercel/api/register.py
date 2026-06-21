from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import os
from vercel_kv import kv

app = Flask(__name__)
CORS(app)

@app.route('/api/register', methods=['POST'])
def register_agent():
    """Enregistre un nouvel agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        info = data.get('info', {})
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if not agent_id:
            return jsonify({'error': 'agent_id required'}), 400
        
        key = f"agent:{agent_id}"
        existing = kv.get(key)
        
        if existing:
            agent_data = json.loads(existing)
        else:
            agent_data = {
                'commands': [],
                'results': [],
                'last_seen': datetime.datetime.now().isoformat(),
                'ip': ip,
                'info': info,
                'created_at': datetime.datetime.now().isoformat()
            }
        
        # Mettre à jour
        agent_data['last_seen'] = datetime.datetime.now().isoformat()
        agent_data['ip'] = ip
        
        # Sauvegarder
        kv.set(key, json.dumps(agent_data))
        
        return jsonify({
            'status': 'registered', 
            'agent_id': agent_id,
            'message': 'Agent registered successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)