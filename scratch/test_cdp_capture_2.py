import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile')
os.makedirs(user_data, exist_ok=True)
os.makedirs('docs/capturas', exist_ok=True)

proc = subprocess.Popen([
    edge_exe,
    '--headless=new',
    '--remote-debugging-port=9222',
    f'--user-data-dir={user_data}',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--window-size=1280,800',
    'about:blank'
])

time.sleep(2)

try:
    req = urllib.request.Request('http://127.0.0.1:9222/json/new?http://127.0.0.1:8000/login/', method='PUT')
    with urllib.request.urlopen(req) as resp:
        tab_info = json.loads(resp.read().decode())
    
    ws_url = tab_info['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=10)
    
    # Wait for page to render
    time.sleep(3)
    
    # Send screenshot command directly
    ws.send(json.dumps({'id': 100, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}))
    
    while True:
        raw = ws.recv()
        msg = json.loads(raw)
        if msg.get('id') == 100:
            img_b64 = msg['result']['data']
            break
            
    out_file = 'docs/capturas/01_login.png'
    with open(out_file, 'wb') as f:
        f.write(base64.b64decode(img_b64))
        
    print(f"SUCCESS! Captured {out_file}, size: {os.path.getsize(out_file)} bytes")
    ws.close()
finally:
    proc.terminate()
