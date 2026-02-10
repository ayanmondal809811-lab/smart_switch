from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)
# Cloud-e command store korar jonno variable
last_command = "none"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Remote</title>
    <style>
        body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .btn { width: 120px; height: 120px; border-radius: 50%; border: none; font-size: 20px; font-weight: bold; cursor: pointer; margin: 10px; transition: 0.3s; }
        .on { background: #2ecc71; box-shadow: 0 0 20px #2ecc7155; }
        .off { background: #e74c3c; box-shadow: 0 0 20px #e74c3c55; }
        .btn:active { transform: scale(0.9); }
    </style>
</head>
<body>
    <h1>CLOUD CONTROL</h1>
    <button class="btn on" onclick="send('0')">ON</button>
    <button class="btn off" onclick="send('1')">OFF</button>
    <p id="stat">Ready</p>

    <script>
        function send(cmd) {
            fetch('/send/' + cmd).then(() => {
                document.getElementById('stat').innerText = "Sent: " + (cmd=='0'?'ON':'OFF');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

# Phone theke command pathano
@app.route('/send/<cmd>')
def send_command(cmd):
    global last_command
    last_command = cmd
    return f"Command {cmd} queued"

# Bridge theke command check kora
@app.route('/get')
def get_command():
    global last_command
    temp = last_command
    last_command = "none" # Command read hoye gele khali kore deya
    return jsonify({"cmd": temp})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)