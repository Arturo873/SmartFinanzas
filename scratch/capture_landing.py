import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_landing')
os.makedirs(user_data, exist_ok=True)

proc = subprocess.Popen([
    edge_exe,
    '--headless=new',
    '--remote-debugging-port=9222',
    f'--user-data-dir={user_data}',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-extensions',
    '--disable-gpu',
    '--run-all-compositor-stages-before-draw',
    '--window-size=1280,850',
    'http://127.0.0.1:8000/'
])

time.sleep(3)

def cdp_send(ws, method, params=None, counter=[1]):
    cid = counter[0]
    counter[0] += 1
    req = {'id': cid, 'method': method}
    if params:
        req['params'] = params
    ws.send(json.dumps(req))
    while True:
        msg = json.loads(ws.recv())
        if msg.get('id') == cid:
            print("Received reply for", cid, method, "keys:", list(msg.keys()), msg.get('error'))
            return msg.get('result', {})

try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
        tabs = json.loads(resp.read().decode())
    
    page_tab = next((t for t in tabs if t.get('type') == 'page'), tabs[0])
    ws = websocket.create_connection(page_tab['webSocketDebuggerUrl'], timeout=10)
    
    time.sleep(2)
    res_shot = cdp_send(ws, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in res_shot:
        with open('docs/capturas/00_landing.png', 'wb') as f:
            f.write(base64.b64decode(res_shot['data']))
        print("Saved 00_landing.png! Size:", os.path.getsize('docs/capturas/00_landing.png'))
    ws.close()
finally:
    proc.terminate()
