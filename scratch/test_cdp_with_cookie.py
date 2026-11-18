import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_test')
os.makedirs(user_data, exist_ok=True)
os.makedirs('docs/capturas', exist_ok=True)

session_key = 'k6jfou743h4ukqbrmv4z3sdil9x4mw3o' # dueno_coagra

proc = subprocess.Popen([
    edge_exe,
    '--headless=new',
    '--remote-debugging-port=9222',
    f'--user-data-dir={user_data}',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--run-all-compositor-stages-before-draw',
    '--window-size=1280,850',
    'http://127.0.0.1:8000/'
])

time.sleep(3)

try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
        tabs = json.loads(resp.read().decode())
    
    ws_url = tabs[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=10)
    
    # Enable Network & Page
    ws.send(json.dumps({'id': 1, 'method': 'Network.enable'}))
    ws.recv()
    ws.send(json.dumps({'id': 2, 'method': 'Page.enable'}))
    ws.recv()
    
    # Set Cookie
    cookie_cmd = {
        'id': 3,
        'method': 'Network.setCookie',
        'params': {
            'name': 'sessionid',
            'value': session_key,
            'domain': '127.0.0.1',
            'path': '/'
        }
    }
    ws.send(json.dumps(cookie_cmd))
    print("setCookie response:", ws.recv()[:100])
    
    # Navigate to dashboard
    ws.send(json.dumps({'id': 4, 'method': 'Page.navigate', 'params': {'url': 'http://127.0.0.1:8000/dashboard/'}}))
    print("Page.navigate response:", ws.recv()[:100])
    
    # Wait for dashboard to fully render Chart.js and components
    time.sleep(3)
    
    # Take screenshot
    ws.send(json.dumps({'id': 5, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}))
    while True:
        m = ws.recv()
        d = json.loads(m)
        if d.get('id') == 5:
            b64 = d['result']['data']
            out_file = 'docs/capturas/03_dashboard_dueno.png'
            with open(out_file, 'wb') as f:
                f.write(base64.b64decode(b64))
            print("Dashboard captured! Size:", os.path.getsize(out_file))
            break
    ws.close()
finally:
    proc.terminate()
