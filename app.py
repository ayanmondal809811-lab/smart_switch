from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)

# কমান্ড কিউ
command_queue = []

# ১২টি ডিভাইসের মেমোরি (পিন ২ থেকে ১৩)
devices = {str(i): {"name": f"Switch {i-1}", "state": 0} for i in range(2, 14)}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkySwitch | OS v1.0</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-blue: #00d2ff;
            --neon-green: #39ff14;
            --neon-pink: #f400ff;
            --bg-dark: #020617;
            --glass: rgba(15, 23, 42, 0.8);
            --border: rgba(0, 210, 255, 0.3);
        }

        * { box-sizing: border-box; }
        body, html {
            margin: 0; padding: 0; height: 100%;
            background: var(--bg-dark);
            color: white;
            font-family: 'Rajdhani', sans-serif;
            overflow: hidden;
        }

        /* --- ফিউচারিস্টিক ব্যাকগ্রাউন্ড --- */
        .bg-vibe {
            position: fixed; width: 100%; height: 100%;
            background: radial-gradient(circle at 50% 50%, #1e293b 0%, #020617 100%);
            z-index: -1;
        }

        /* --- Intro Layer --- */
        #intro-layer {
            position: fixed; inset: 0; background: black;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 9999; transition: all 1.2s cubic-bezier(0.8, 0, 0.2, 1);
        }

        .power-btn {
            position: relative; width: 120px; height: 120px;
            border-radius: 50%; border: 4px solid var(--neon-blue);
            background: transparent; color: var(--neon-blue);
            font-size: 50px; cursor: pointer;
            box-shadow: 0 0 30px var(--neon-blue), inset 0 0 15px var(--neon-blue);
            transition: 0.4s; z-index: 2;
        }

        .power-btn:hover {
            box-shadow: 0 0 60px var(--neon-blue), inset 0 0 30px var(--neon-blue);
            transform: scale(1.1);
        }

        .sky-text {
            margin-top: 30px; font-family: 'Orbitron'; font-size: 2.5rem;
            letter-spacing: 15px; text-transform: uppercase;
            color: var(--neon-blue); text-shadow: 0 0 20px var(--neon-blue);
            opacity: 0; transform: translateY(30px); transition: 1s ease-out;
        }

        /* --- Main Hub UI --- */
        #main-hub {
            opacity: 0; transform: scale(0.9); transition: 1.5s ease-out;
            padding: 20px; height: 100vh; overflow-y: auto;
        }

        header {
            text-align: center; padding: 20px 0 40px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 40px;
        }

        header h1 {
            font-family: 'Orbitron'; font-size: 2rem; margin: 0;
            background: linear-gradient(to right, #fff, var(--neon-blue));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: 8px;
        }

        .grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 25px; max-width: 1200px; margin: 0 auto;
        }

        .card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 15px; padding: 25px;
            position: relative; overflow: hidden;
            backdrop-filter: blur(15px);
            transition: 0.4s;
        }

        .card:hover {
            border-color: var(--neon-blue);
            box-shadow: 0 0 25px rgba(0, 210, 255, 0.2);
            transform: translateY(-5px);
        }

        .icon-box {
            font-size: 40px; margin-bottom: 15px; color: #1e293b;
            transition: 0.4s;
        }

        .active .icon-box {
            color: var(--neon-green);
            text-shadow: 0 0 20px var(--neon-green);
        }

        .dev-name {
            background: transparent; border: none; color: white;
            font-family: 'Orbitron'; font-size: 1rem; text-align: center;
            width: 100%; margin-bottom: 20px; border-bottom: 1px solid transparent;
        }

        .dev-name:focus { outline: none; border-bottom: 1px solid var(--neon-blue); }

        .toggle-btn {
            width: 100%; padding: 12px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.05); color: #64748b;
            font-weight: bold; cursor: pointer; border-radius: 5px;
            font-family: 'Orbitron'; font-size: 0.8rem; transition: 0.3s;
        }

        .active .toggle-btn {
            background: var(--neon-green); color: black;
            box-shadow: 0 0 15px var(--neon-green); border: none;
        }

        /* স্ক্যানিং লাইন এনিমেশন */
        .scan-line {
            position: absolute; width: 100%; height: 2px;
            background: rgba(0, 210, 255, 0.5); top: 0; left: 0;
            animation: scan 3s linear infinite; opacity: 0.2;
        }

        @keyframes scan {
            0% { top: 0; } 100% { top: 100%; }
        }

        /* সাউন্ড বাটন ইফেক্ট */
        .toggle-btn:active { transform: scale(0.95); }

    </style>
</head>
<body>

    <div class="bg-vibe"></div>

    <div id="intro-layer">
        <button class="power-btn" onclick="initSystem()">
            <i class="fas fa-power-off"></i>
        </button>
        <div class="sky-text" id="skyText">SkySwitch</div>
    </div>

    <div id="main-hub">
        <header>
            <h1><i class="fas fa-microchip"></i> SKYSWITCH HUB</h1>
            <p style="color: var(--neon-blue); letter-spacing: 2px; font-size: 12px;">SYSTEM STATUS: <span id="online-status">SCANNING...</span></p>
        </header>

        <div class="grid" id="deviceGrid"></div>
    </div>

    <audio id="audioStartup" src="/static/startup.mp3"></audio>
    <audio id="audioClick" src="/static/click.mp3"></audio>

    <script>
        const audioStartup = document.getElementById('audioStartup');
        const audioClick = document.getElementById('audioClick');

        function initSystem() {
            // সাউন্ড প্লে
            audioStartup.play().catch(e => console.log("Audio play failed"));
            
            // এনিমেশন শুরু
            const text = document.getElementById('skyText');
            text.style.opacity = "1";
            text.style.transform = "translateY(0)";
            
            setTimeout(() => {
                const intro = document.getElementById('intro-layer');
                const hub = document.getElementById('main-hub');
                
                intro.style.transform = "translateY(-100%)";
                hub.style.opacity = "1";
                hub.style.transform = "scale(1)";
                
                document.getElementById('online-status').innerText = "ENCRYPTED & ONLINE";
            }, 3000);

            loadDevices();
        }

        async function loadDevices() {
            const res = await fetch('/status');
            const devices = await res.json();
            const grid = document.getElementById('deviceGrid');
            grid.innerHTML = '';

            for (const [pin, info] of Object.entries(devices)) {
                const isActive = info.state == 1;
                grid.innerHTML += `
                    <div class="card ${isActive ? 'active' : ''}">
                        <div class="scan-line"></div>
                        <div class="icon-box">
                            <i class="fas ${isActive ? 'fa-lightbulb' : 'fa-regular fa-lightbulb'}"></i>
                        </div>
                        <input type="text" class="dev-name" value="${info.name}" onchange="rename('${pin}', this.value)">
                        <button class="toggle-btn" onclick="toggle('${pin}', ${isActive ? 0 : 1})">
                            ${isActive ? 'SYSTEM ACTIVE' : 'ENGAGE'}
                        </button>
                    </div>
                `;
            }
        }

        function toggle(pin, state) {
            audioClick.currentTime = 0;
            audioClick.play();
            fetch(`/send/${pin}/${state}`).then(() => loadDevices());
        }

        function rename(pin, newName) {
            fetch(`/rename/${pin}/${newName}`);
        }

        // অটো আপডেট (৫ সেকেন্ড পর পর)
        setInterval(loadDevices, 5000);
    </script>
</body>
</html>
"""

# --- Flask Routes (অপরিবর্তিত) ---

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/send/<pin>/<state>')
def send_command(pin, state):
    global command_queue, devices
    if pin in devices:
        devices[pin]['state'] = int(state)
        cmd_str = f"{pin}:{state}"
        command_queue.append(cmd_str)
        return jsonify({"status": "queued", "cmd": cmd_str})
    return jsonify({"error": "Invalid Pin"}), 400

@app.route('/rename/<pin>/<name>')
def rename_device(pin, name):
    if pin in devices:
        devices[pin]['name'] = name
        return jsonify({"status": "renamed", "name": name})
    return jsonify({"error": "Invalid Pin"}), 400

@app.route('/status')
def get_status():
    return jsonify(devices)

@app.route('/get')
def get_command():
    global command_queue
    if command_queue:
        return jsonify({"cmd": command_queue.pop(0)})
    return jsonify({"cmd": "none"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)