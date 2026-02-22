from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app) # Cloud access allow korar jonno
app.secret_key = 'sky_switch_secret_key_123'

# --- Data Storage ---
command_queue = []
# ESP8266 D0-D8 Mapping: 16, 5, 4, 0, 2, 14, 12, 13, 15
pins = ["16", "5", "4", "0", "2", "14", "12", "13", "15"]
devices = {p: {"name": f"Switch D{pins.index(p)}", "state": 0} for p in pins}

# --- UI (HTML/CSS/JS) ---
HUB_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SkySwitch Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root { --blue: #00d2ff; --green: #39ff14; --bg: #020617; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; max-width: 1000px; margin: 0 auto; }
        .card { background: rgba(255,255,255,0.05); border: 1px solid var(--blue); border-radius: 15px; padding: 20px; transition: 0.3s; }
        .active { border-color: var(--green); box-shadow: 0 0 15px var(--green); }
        button { width: 100%; padding: 12px; margin-top: 10px; cursor: pointer; font-weight: bold; border-radius: 8px; border: 1px solid var(--blue); background: transparent; color: var(--blue); }
        .on { background: var(--green); color: black; border: none; }
        h1 { font-size: 2rem; letter-spacing: 3px; color: var(--blue); margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>SKYSWITCH HUB</h1>
    <div class="grid" id="grid"></div>
    <script>
        async function load() {
            try {
                const r = await fetch('/status');
                const data = await r.json();
                const g = document.getElementById('grid');
                g.innerHTML = '';
                for (const [pin, info] of Object.entries(data)) {
                    const isOn = info.state == 1;
                    g.innerHTML += `<div class="card ${isOn?'active':''}">
                        <h3>${info.name}</h3>
                        <button onclick="toggle('${pin}', ${isOn?0:1})" class="${isOn?'on':''}">
                            ${isOn?'TURN OFF':'TURN ON'}
                        </button>
                    </div>`;
                }
            } catch (e) { console.log("Error loading status"); }
        }
        function toggle(p, s) { fetch(`/send/${p}/${s}`).then(load); }
        setInterval(load, 3000); load();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HUB_HTML)

@app.route('/status')
def get_status(): return jsonify(devices)

@app.route('/send/<pin>/<state>')
def send_cmd(pin, state):
    if pin in devices:
        devices[pin]['state'] = int(state)
        command_queue.append(f"{pin}:{state}")
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400

@app.route('/get')
def get_cmd():
    if command_queue: return jsonify({"cmd": command_queue.pop(0)})
    return jsonify({"cmd": "none"})

if __name__ == '__main__':
    # Render-e site open na hobar prodhan karon holo port thikmoto na pawa
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)