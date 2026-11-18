import subprocess, os, tempfile

temp_dir = tempfile.mkdtemp()
out_png = os.path.abspath('docs/capturas/test_edge.png')
edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

cmd = [
    edge_exe,
    '--headless',
    '--disable-gpu',
    f'--user-data-dir={temp_dir}',
    f'--screenshot={out_png}',
    '--window-size=1280,800',
    'http://127.0.0.1:8000/login/'
]

print("Running command:", cmd)
res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
print("Return code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)
print("File exists?", os.path.exists(out_png))
if os.path.exists(out_png):
    print("Size:", os.path.getsize(out_png))
