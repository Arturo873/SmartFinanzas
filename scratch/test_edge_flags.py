import subprocess, os, tempfile

out_png = os.path.abspath('docs/capturas/test_login.png')
os.makedirs(os.path.dirname(out_png), exist_ok=True)
edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

# Try with --headless=new, --no-sandbox, --disable-extensions
cmd = [
    edge_exe,
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-dev-shm-usage',
    f'--screenshot={out_png}',
    '--window-size=1280,800',
    '--default-background-color=00000000',
    'http://127.0.0.1:8000/login/'
]

print("Running command:", cmd)
try:
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
    print("Returncode:", res.returncode)
    print("Stdout:", res.stdout)
    print("Stderr:", res.stderr)
except subprocess.TimeoutExpired:
    print("Timed out!")

print("File exists?", os.path.exists(out_png))
if os.path.exists(out_png):
    print("File size:", os.path.getsize(out_png))
