from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import redis
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Connexion à Upstash Redis avec gestion d'erreur
def get_redis_client():
    try:
        redis_url = os.environ.get("UPSTASH_REDIS_REST_URL")
        if not redis_url:
            # Fallback pour le développement local
            redis_url = "redis://localhost:6379"
        return redis.from_url(redis_url)
    except Exception as e:
        print(f"Erreur de connexion Redis: {e}")
        return None

redis_client = get_redis_client()

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Récupère la liste de tous les agents"""
    try:
        if not redis_client:
            return jsonify({"error": "Redis not connected"}), 500
        
        # Récupérer toutes les clés des agents
        keys = redis_client.keys("agent:*")
        agents = {}
        
        for key in keys:
            agent_id = key.decode('utf-8').replace("agent:", "")
            data = redis_client.get(key)
            if data:
                agents[agent_id] = json.loads(data.decode('utf-8'))
        
        return jsonify(agents)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
