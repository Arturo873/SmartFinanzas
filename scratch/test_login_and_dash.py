import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_dueno')
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
    'http://127.0.0.1:8000/login/'
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
            return msg.get('result', {})

try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
        tabs = json.loads(resp.read().decode())
    
    ws_url = tabs[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=10)
    
    # 1. Fill login form
    js_login = """
    document.querySelector('input[name="username"]').value = 'dueno_coagra';
    document.querySelector('input[name="password"]').value = 'SmartFinanzas2026!';
    document.querySelector('button[type="submit"], input[type="submit"]').click();
    """
    cdp_send(ws, 'Runtime.evaluate', {'expression': js_login})
    print("Submitted login form, waiting 4s for dashboard redirect...")
    time.sleep(4)
    
    # Check current URL and title
    title_res = cdp_send(ws, 'Runtime.evaluate', {'expression': 'document.title + " | " + window.location.href'})
    print("Current page:", title_res['result']['value'])
    
    # 2. Capture screenshot of Dashboard
    res_shot = cdp_send(ws, 'Page.captureScreenshot', {'format': 'png'})
    b64 = res_shot['data']
    
    out_file = 'docs/capturas/03_dashboard_dueno.png'
    with open(out_file, 'wb') as f:
        f.write(base64.b64decode(b64))
        
    print(f"SUCCESS! Dashboard captured: {out_file}, size: {os.path.getsize(out_file)} bytes")
    ws.close()
finally:
    proc.terminate()
