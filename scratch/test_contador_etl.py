import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_contador')
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
    
    page_tab = next((t for t in tabs if t.get('type') == 'page'), tabs[0])
    ws = websocket.create_connection(page_tab['webSocketDebuggerUrl'], timeout=10)
    
    # 1. Fill login as contador
    js_login = """
    document.querySelector('input[name="email"]').value = 'contador@coagra.cl';
    document.querySelector('input[name="password"]').value = 'SmartFinanzas2026!';
    document.querySelector('button[type="submit"], input[type="submit"]').click();
    """
    cdp_send(ws, 'Runtime.evaluate', {'expression': js_login})
    print("Submitted login form as contador, waiting 4s...")
    time.sleep(4)
    
    title_res = cdp_send(ws, 'Runtime.evaluate', {'expression': 'document.title + " | " + window.location.href'})
    print("Current page:", title_res['result']['value'])
    
    # Navigate to /etl/carga/
    cdp_send(ws, 'Page.navigate', {'url': 'http://127.0.0.1:8000/etl/carga/'})
    time.sleep(3)
    
    page_etl = cdp_send(ws, 'Runtime.evaluate', {'expression': 'document.title + " | " + window.location.href'})
    print("ETL page:", page_etl['result']['value'])
    
    # Capture ETL Carga
    res_shot = cdp_send(ws, 'Page.captureScreenshot', {'format': 'png'})
    b64 = res_shot['data']
    with open('docs/capturas/11_etl_carga.png', 'wb') as f:
        f.write(base64.b64decode(b64))
    print("Saved 11_etl_carga.png! Size:", os.path.getsize('docs/capturas/11_etl_carga.png'))
    
    # Navigate to /etl/ratios/
    cdp_send(ws, 'Page.navigate', {'url': 'http://127.0.0.1:8000/etl/ratios/'})
    time.sleep(3)
    res_shot2 = cdp_send(ws, 'Page.captureScreenshot', {'format': 'png'})
    with open('docs/capturas/12_etl_ratios.png', 'wb') as f:
        f.write(base64.b64decode(res_shot2['data']))
    print("Saved 12_etl_ratios.png! Size:", os.path.getsize('docs/capturas/12_etl_ratios.png'))
    
    # Navigate to /etl/historial/
    cdp_send(ws, 'Page.navigate', {'url': 'http://127.0.0.1:8000/etl/historial/'})
    time.sleep(3)
    res_shot3 = cdp_send(ws, 'Page.captureScreenshot', {'format': 'png'})
    with open('docs/capturas/13_etl_historial.png', 'wb') as f:
        f.write(base64.b64decode(res_shot3['data']))
    print("Saved 13_etl_historial.png! Size:", os.path.getsize('docs/capturas/13_etl_historial.png'))
    
    ws.close()
finally:
    proc.terminate()
