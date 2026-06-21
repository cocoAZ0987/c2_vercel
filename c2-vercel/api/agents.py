from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from vercel_kv import kv

app = Flask(__name__)
CORS(app)

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Récupère la liste de tous les agents"""
    try:
        # Récupérer toutes les clés des agents
        keys = kv.keys("agent:*")
        agents = {}
        
        for key in keys:
            agent_id = key.replace("agent:", "")
            data = kv.get(key)
            if data:
                agents[agent_id] = json.loads(data)
        
        return jsonify(agents)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(request):
    return app(request)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)