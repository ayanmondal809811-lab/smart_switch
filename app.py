from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)

# কমান্ড কিউ (যাতে কমান্ড হারিয়ে না যায়)
command_queue = []

# ডিভাইসের ডিফল্ট নাম এবং স্ট্যাটাস মেমোরিতে রাখা
devices = {str(i): {"name": f"Device {i}", "state": 0} for i in range(2, 14)}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Home Hub</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f1f5f9; --accent: #3b82f6; --success: #22c55e; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
        h1 { text-align: center; font-weight: 300; letter-spacing: 2px; margin-bottom: 30px; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; max-width: 800px; margin: 0 auto; }
        
        .card { background: var(--card); border-radius: 15px; padding: 20px; text-align: center; transition: 0.3s; position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card:hover { transform: translateY(-5px); }
        
        .icon-box { font-size: 30px; margin-bottom: 10px; color: #64748b; transition: 0.3s; }
        .active .icon-box { color: var(--success); text-shadow: 0 0 15px rgba(34, 197, 94, 0.5); }
        
        input.dev-name { background: transparent; border: none; color: var(--text); text-align: center; font-size: 16px; width: 100%; margin-bottom: 10px; padding: 5px; border-bottom: 1px solid transparent; }
        input.dev-name:focus { border-bottom: 1px solid var(--accent); outline: none; }
        
        .toggle-btn { width: 100%; padding: 10px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; background: #334155; color: #94a3b8; transition: 0.3s; }
        .active .toggle-btn { background: var(--success); color: white; }

        /* Save Button for Names */
        .save-hint { font-size: 10px; color: var(--accent); opacity: 0; transition: 0.3s; }
        .editing .save-hint { opacity: 1; }
    </style>
</head>
<body>
    <h1><i class="fas fa-network-wired"></i> SMART HUB</h1>
    
    <div class="grid" id="deviceGrid">
        </div>

    <script>
        // সার্ভার থেকে ডিভাইসের লিস্ট আনা
        async function loadDevices() {
            const res = await fetch('/status');
            const devices = await res.json();
            const grid = document.getElementById('deviceGrid');
            grid.innerHTML = '';

            for (const [pin, info] of Object.entries(devices)) {
                const isActive = info.state == 1;
                grid.innerHTML += `
                    <div class="card ${isActive ? 'active' : ''}" id="card-${pin}">
                        <div class="icon-box"><i class="fas fa-lightbulb"></i></div>
                        <input type="text" class="dev-name" value="${info.name}" onchange="rename('${pin}', this.value)" onfocus="this.parentElement.classList.add('editing')" onblur="this.parentElement.classList.remove('editing')">
                        <div class="save-hint">Auto Saving...</div>
                        <button class="toggle-btn" onclick="toggle('${pin}', ${isActive ? 0 : 1})">
                            ${isActive ? 'ON' : 'OFF'}
                        </button>
                    </div>
                `;
            }
        }

        // কমান্ড পাঠানো
        function toggle(pin, state) {
            fetch(`/send/${pin}/${state}`).then(() => loadDevices());
        }

        // নাম পরিবর্তন করা
        function rename(pin, newName) {
            fetch(`/rename/${pin}/${newName}`);
        }

        // পেজ লোড হলে এবং প্রতি ৩ সেকেন্ডে আপডেট
        loadDevices();
        setInterval(loadDevices, 3000); 
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

# কমান্ড পাঠানোর রুট
@app.route('/send/<pin>/<state>')
def send_command(pin, state):
    global command_queue, devices
    
    if pin in devices:
        devices[pin]['state'] = int(state) # সার্ভারে স্টেট আপডেট
        # আর্ডুইনোর জন্য ফরম্যাট: "pin:state"
        cmd_str = f"{pin}:{state}"
        command_queue.append(cmd_str)
        return jsonify({"status": "queued", "cmd": cmd_str})
    return jsonify({"error": "Invalid Pin"}), 400

# নাম রিনেম করার রুট
@app.route('/rename/<pin>/<name>')
def rename_device(pin, name):
    if pin in devices:
        devices[pin]['name'] = name
        return jsonify({"status": "renamed", "name": name})
    return jsonify({"error": "Invalid Pin"}), 400

# অ্যাপের বর্তমান অবস্থা জানার রুট (ফ্রন্টএন্ডের জন্য)
@app.route('/status')
def get_status():
    return jsonify(devices)

# ব্রিজ (পাইথন) এই রুটে হিট করে কমান্ড নিয়ে যাবে
@app.route('/get')
def get_command():
    global command_queue
    if command_queue:
        # লিস্ট থেকে প্রথম কমান্ড বের করে আনা (FIFO)
        cmd = command_queue.pop(0)
        return jsonify({"cmd": cmd})
    else:
        return jsonify({"cmd": "none"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)