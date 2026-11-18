import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_clean')
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
    '--run-all-compositor-stages-before-draw',
    '--window-size=1280,850',
    'about:blank'
])

time.sleep(2)

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
            return msg.get('result', {})

try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
        tabs = json.loads(resp.read().decode())
    
    ws_url = tabs[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=10)
    
    session_key = 'k6jfou743h4ukqbrmv4z3sdil9x4mw3o' # dueno_coagra
    
    # 1. Set Cookie directly
    res_cookie = cdp_send(ws, 'Network.setCookie', {
        'name': 'sessionid',
        'value': session_key,
        'domain': '127.0.0.1',
        'path': '/'
    })
    print("Cookie set result:", res_cookie)
    
    # 2. Navigate to dashboard
    res_nav = cdp_send(ws, 'Page.navigate', {'url': 'http://127.0.0.1:8000/dashboard/'})
    print("Navigated to dashboard:", res_nav)
    
    # Wait for Chart.js rendering
    time.sleep(4)
    
    # 3. Capture screenshot
    res_shot = cdp_send(ws, 'Page.captureScreenshot', {'format': 'png'})
    b64 = res_shot['data']
    
    out_file = 'docs/capturas/03_dashboard_dueno.png'
    with open(out_file, 'wb') as f:
        f.write(base64.b64decode(b64))
        
    print(f"SUCCESS! Captured {out_file}, size: {os.path.getsize(out_file)} bytes")
    ws.close()
finally:
    proc.terminate()
