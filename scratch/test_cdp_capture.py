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
    # 1. Create a new target/tab pointing to login
    req = urllib.request.Request('http://127.0.0.1:9222/json/new?http://127.0.0.1:8000/login/', method='PUT')
    with urllib.request.urlopen(req) as resp:
        tab_info = json.loads(resp.read().decode())
    
    ws_url = tab_info['webSocketDebuggerUrl']
    print("Tab opened. WS URL:", ws_url)
    
    ws = websocket.create_connection(ws_url, timeout=10)
    
    # Enable Page domain
    ws.send(json.dumps({'id': 1, 'method': 'Page.enable'}))
    ws.recv()
    
    # Wait for page load
    time.sleep(2)
    
    # Capture screenshot
    ws.send(json.dumps({'id': 2, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}))
    
    while True:
        resp = json.loads(ws.recv())
        if resp.get('id') == 2:
            img_b64 = resp['result']['data']
            break
            
    out_file = 'docs/capturas/01_login.png'
    with open(out_file, 'wb') as f:
        f.write(base64.b64decode(img_b64))
        
    print(f"SUCCESS! Captured {out_file}, size: {os.path.getsize(out_file)} bytes")
    ws.close()
finally:
    proc.terminate()
    print("Edge terminated.")
