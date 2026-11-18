import subprocess, time, urllib.request, json, os

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
    'about:blank'
])

print("Edge PID:", proc.pid)
time.sleep(2)

try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json/version', timeout=5) as resp:
        data = json.loads(resp.read().decode())
        print("Edge CDP version info:", data)
finally:
    proc.terminate()
    print("Edge terminated.")
