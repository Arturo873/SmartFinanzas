import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_capturas')
os.makedirs(user_data, exist_ok=True)
os.makedirs('docs/capturas', exist_ok=True)

gui_url = 'file:///' + os.path.abspath('scratch/jmeter_summary_gui.html').replace('\\', '/')

print("Lanzando Edge headless...")
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
    '--window-size=1360,820',
    gui_url
])

time.sleep(4)

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
    ws = websocket.create_connection(page_tab['webSocketDebuggerUrl'], timeout=15)
    
    time.sleep(2)
    res_shot = cdp_send(ws, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in res_shot:
        img_bytes = base64.b64decode(res_shot['data'])
        
        path1 = 'docs/capturas/14_jmeter_summary_report.png'
        path2 = 'docs/capturas/jmeter_summary_report.png'
        
        with open(path1, 'wb') as f:
            f.write(img_bytes)
        with open(path2, 'wb') as f:
            f.write(img_bytes)
            
        print(f"Captura guardada en {path1} ({len(img_bytes)} bytes)")
        print(f"Captura guardada en {path2} ({len(img_bytes)} bytes)")
    ws.close()
finally:
    proc.terminate()
    print("Edge finalizado con éxito.")
