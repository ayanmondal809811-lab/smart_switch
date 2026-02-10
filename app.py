from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Arduino Remote</title>
    <style>
        body { background: #0f0f0f; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .box { background: #1a1a1a; padding: 40px; border-radius: 30px; text-align: center; border: 1px solid #333; }
        .btn { width: 120px; height: 120px; border-radius: 50%; border: none; font-size: 20px; font-weight: bold; cursor: pointer; margin: 15px; transition: 0.3s; }
        .on { background: #2ecc71; box-shadow: 0 0 20px #2ecc7155; color: white; }
        .off { background: #e74c3c; box-shadow: 0 0 20px #e74c3c55; color: white; }
        .btn:active { transform: scale(0.9); }
        #status { margin-top: 20px; color: #555; font-size: 14px; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="color: #888; letter-spacing: 3px;">CLOUD REMOTE</h2>
        <button class="btn on" onclick="send('0')">ON</button>
        <button class="btn off" onclick="send('1')">OFF</button>
        <div id="status">Connecting to Cloud...</div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script>
        const socket = io();
        socket.on('connect', () => { document.getElementById('status').innerText = "Cloud Online"; });
        function send(cmd) {
            socket.emit('web_command', cmd);
            document.getElementById('status').innerText = "Sent: " + (cmd === '0' ? 'ON' : 'OFF');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@socketio.on('web_command')
def handle_web_command(cmd):
    print(f"Relaying command: {cmd}")
    # Eita bridge.py-r kache signal pathabe
    emit('bridge_control', cmd, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)