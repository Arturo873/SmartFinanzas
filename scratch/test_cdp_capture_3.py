import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile')
os.makedirs(user_data, exist_ok=True)

proc = subprocess.Popen([
    edge_exe,
    '--headless=new',
    '--remote-debugging-port=9222',
    f'--user-data-dir={user_data}',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--run-all-compositor-stages-before-draw',
    '--window-size=1280,800',
    'http://127.0.0.1:8000/login/'
])

time.sleep(3)

try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
        tabs = json.loads(resp.read().decode())
    print("Open tabs count:", len(tabs))
    
    ws_url = tabs[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=10)
    
    ws.send(json.dumps({'id': 1, 'method': 'Page.enable'}))
    print("Page.enable:", ws.recv()[:100])
    
    # Also evaluate a quick JS to check if DOM is ready
    ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.title'}}))
    print("Runtime.evaluate:", ws.recv()[:100])
    
    ws.send(json.dumps({'id': 3, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}))
    print("Sent Page.captureScreenshot...")
    while True:
        m = ws.recv()
        data = json.loads(m)
        if data.get('id') == 3:
            b64 = data['result']['data']
            print("SUCCESS! Got screenshot bytes:", len(b64))
            with open('docs/capturas/test_screenshot.png', 'wb') as f:
                f.write(base64.b64decode(b64))
            print("File saved! Size:", os.path.getsize('docs/capturas/test_screenshot.png'))
            break
    ws.close()
finally:
    proc.terminate()
