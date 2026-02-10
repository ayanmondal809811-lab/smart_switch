from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
# Ping timeout ebong interval barano hoyeche jate connection drop na hoy
socketio = SocketIO(app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Switch</title>
    <style>
        body { background: #000; color: #fff; text-align: center; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
        .btn { width: 120px; height: 120px; border-radius: 50%; border: none; font-size: 20px; font-weight: bold; cursor: pointer; margin: 20px; }
        .on { background: #2ecc71; } .off { background: #e74c3c; }
    </style>
</head>
<body>
    <h1>SMART SWITCH</h1>
    <button class="btn on" onclick="s('0')">ON</button>
    <button class="btn off" onclick="s('1')">OFF</button>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script>
        const socket = io();
        function s(c) { socket.emit('web_msg', c); }
        socket.on('connect', () => console.log('Connected to Server'));
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@socketio.on('web_msg')
def handle_msg(data):
    print(f"Server received: {data}")
    # 'broadcast=True' dilei sudhu bridge.py pabe
    emit('to_bridge', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)