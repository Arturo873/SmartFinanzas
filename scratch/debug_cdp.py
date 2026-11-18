import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile')
os.makedirs(user_data, exist_ok=True)

proc = subprocess.Popen([
    edge_exe,
    '--headless',
    '--remote-debugging-port=9222',
    f'--user-data-dir={user_data}',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--window-size=1280,800',
    'http://127.0.0.1:8000/login/'
])

time.sleep(3)

try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
        tabs = json.loads(resp.read().decode())
    print("Open tabs count:", len(tabs))
    for t in tabs:
        print("Tab:", t.get('title'), t.get('url'), t.get('webSocketDebuggerUrl'))
    
    ws_url = tabs[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=5)
    
    # Send a simple command
    ws.send(json.dumps({'id': 1, 'method': 'Page.enable'}))
    print("Sent Page.enable, waiting recv...")
    msg1 = ws.recv()
    print("Recv 1:", msg1[:200])
    
    ws.send(json.dumps({'id': 2, 'method': 'Page.captureScreenshot'}))
    print("Sent Page.captureScreenshot, waiting recv...")
    while True:
        m = ws.recv()
        data = json.loads(m)
        print("Recv ID/Method:", data.get('id'), data.get('method'))
        if data.get('id') == 2:
            b64 = data['result']['data']
            print("Got screenshot! Length:", len(b64))
            with open('docs/capturas/test_screenshot.png', 'wb') as f:
                f.write(base64.b64decode(b64))
            print("Saved docs/capturas/test_screenshot.png successfully!")
            break
    ws.close()
finally:
    proc.terminate()
