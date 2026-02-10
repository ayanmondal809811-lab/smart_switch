from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)
command_queue = []

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Home Pro</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #38bdf8; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; }
        h1 { text-align: center; color: var(--accent); letter-spacing: 2px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
        .switch-card { background: var(--card); padding: 20px; border-radius: 20px; text-align: center; border: 1px solid #334155; transition: 0.3s; }
        .switch-card:active { transform: scale(0.95); }
        .name-input { background: transparent; border: none; color: white; text-align: center; font-size: 16px; width: 100%; margin-bottom: 10px; border-bottom: 1px solid #334155; }
        .btn { width: 60px; height: 60px; border-radius: 50%; border: none; cursor: pointer; font-size: 20px; transition: 0.3s; }
        .on { background: #22c55e; box-shadow: 0 0 15px #22c55e55; color: white; }
        .off { background: #ef4444; box-shadow: 0 0 15px #ef444455; color: white; margin-left: 10px; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-microchip"></i> SMART CONTROL</h1>
        <div id="grid" class="grid"></div>
    </div>

    <script>
        const grid = document.getElementById('grid');
        // Pin 2 to 13 setup
        for (let i = 2; i <= 13; i++) {
            const savedName = localStorage.getItem('pin_' + i) || 'Switch ' + (i - 1);
            grid.innerHTML += `
                <div class="switch-card">
                    <input class="name-input" id="name_${i}" value="${savedName}" onchange="saveName(${i}, this.value)">
                    <p style="font-size: 10px; color: #64748b;">PIN D${i}</p>
                    <button class="btn on" onclick="send(${i}, 1)"><i class="fas fa-power-off"></i></button>
                    <button class="btn off" onclick="send(${i}, 0)"><i class="fas fa-times"></i></button>
                </div>
            `;
        }

        function saveName(pin, name) { localStorage.setItem('pin_' + pin, name); }

        function send(pin, state) {
            fetch(`/send/${pin}_${state}`).then(() => {
                console.log(`Pin ${pin} set to ${state}`);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/send/<cmd>')
def send_command(cmd):
    command_queue.append(cmd)
    return "Queued"

@app.route('/get')
def get_command():
    global command_queue
    if command_queue:
        return jsonify({"cmds": command_queue.pop(0)})
    return jsonify({"cmds": "none"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000))