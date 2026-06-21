from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import os
import redis

app = Flask(__name__)
CORS(app)

# Connexion à Upstash Redis
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

@app.route('/api/register', methods=['POST'])
def register_agent():
    """Enregistre un nouvel agent"""
    try:
        if not redis_client:
            return jsonify({'error': 'Redis not connected'}), 500
        
        data = request.json
        agent_id = data.get('agent_id')
        info = data.get('info', {})
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if not agent_id:
            return jsonify({'error': 'agent_id required'}), 400
        
        key = f"agent:{agent_id}"
        existing = redis_client.get(key)
        
        if existing:
            agent_data = json.loads(existing.decode('utf-8'))
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
        redis_client.set(key, json.dumps(agent_data))
        
        return jsonify({
            'status': 'registered', 
            'agent_id': agent_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
