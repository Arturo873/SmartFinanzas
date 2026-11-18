import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_capturas')
os.makedirs(user_data, exist_ok=True)
capturas_dir = os.path.abspath('docs/capturas')
os.makedirs(capturas_dir, exist_ok=True)

class CDPCapturer:
    def __init__(self):
        self.proc = subprocess.Popen([
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
        time.sleep(3)
        with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
            tabs = json.loads(resp.read().decode())
        self.ws_url = tabs[0]['webSocketDebuggerUrl']
        self.ws = websocket.create_connection(self.ws_url, timeout=15)
        self.msg_id = 0
        self._send({'method': 'Page.enable'})

    def _send(self, payload):
        self.msg_id += 1
        payload['id'] = self.msg_id
        self.ws.send(json.dumps(payload))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == self.msg_id:
                return m

    def navigate(self, url, wait_sec=2.5):
        self._send({'method': 'Page.navigate', 'params': {'url': url}})
        time.sleep(wait_sec)

    def evaluate(self, js_expr):
        return self._send({'method': 'Runtime.evaluate', 'params': {'expression': js_expr}})

    def scroll_to(self, y):
        self.evaluate(f'window.scrollTo(0, {y});')
        time.sleep(0.5)

    def login(self, username, password='SmartFinanzas2026!'):
        self.navigate('http://127.0.0.1:8000/logout/', wait_sec=1.0)
        self.navigate('http://127.0.0.1:8000/login/', wait_sec=1.5)
        js = f"""
        document.querySelector('input[name="username"]').value = '{username}';
        document.querySelector('input[name="password"]').value = '{password}';
        document.querySelector('button[type="submit"], input[type="submit"]').click();
        """
        self.evaluate(js)
        time.sleep(3.0)

    def capture(self, filename, clip=None):
        params = {'format': 'png'}
        if clip:
            params['clip'] = clip
        res = self._send({'method': 'Page.captureScreenshot', 'params': params})
        b64 = res['result']['data']
        out_path = os.path.join(capturas_dir, filename)
        with open(out_path, 'wb') as f:
            f.write(base64.b64decode(b64))
        print(f"Captured: {filename} ({os.path.getsize(out_path)} bytes)")
        return out_path

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()


def main():
    print("Iniciando motor de capturas CDP...")
    cap = CDPCapturer()
    try:
        # 1. Login
        print("1. Capturando pantalla de Login...")
        cap.navigate('http://127.0.0.1:8000/logout/', wait_sec=1.0)
        cap.navigate('http://127.0.0.1:8000/login/', wait_sec=2.0)
        cap.capture('01_login.png')

        # 2. Registro
        print("2. Capturando pantalla de Registro...")
        cap.navigate('http://127.0.0.1:8000/registro/', wait_sec=2.0)
        cap.capture('02_registro.png')

        # 3. Rol Dueño: Dashboard General
        print("3. Iniciando sesión como Dueño (dueno_coagra)...")
        cap.login('dueno_coagra')
        cap.navigate('http://127.0.0.1:8000/dashboard/', wait_sec=3.0)
        cap.capture('03_dashboard_general.png')

        # 4. Dashboard: Gráfico de Tendencias y Explicabilidad SHAP (scroll hacia abajo)
        print("4. Capturando gráfico de tendencia y SHAP...")
        cap.scroll_to(450)
        cap.capture('04_dashboard_tendencia_shap.png')

        # 5. Dashboard Predictivo (información predictiva a 90 días)
        print("5. Capturando Dashboard Predictivo...")
        cap.navigate('http://127.0.0.1:8000/dashboard/predictivo/', wait_sec=3.0)
        cap.capture('05_dashboard_predictivo.png')

        # 6. Rol Trabajador: Punto de Venta (Registro de Ventas)
        print("6. Iniciando sesión como Trabajador (trabajador_coagra)...")
        cap.login('trabajador_coagra')
        cap.navigate('http://127.0.0.1:8000/transaccional/ventas/nueva/', wait_sec=2.5)
        # Rellenar un ejemplo en vivo para que la captura se vea realista
        js_venta = """
        const elBruto = document.getElementById('id_gross_total');
        if (elBruto) { elBruto.value = '45000'; elBruto.dispatchEvent(new Event('input')); }
        const elDesc = document.getElementById('id_discount_amount');
        if (elDesc) { elDesc.value = '5000'; elDesc.dispatchEvent(new Event('input')); }
        const elMetodo = document.getElementById('id_payment_method');
        if (elMetodo && elMetodo.options.length > 1) { elMetodo.selectedIndex = 1; elMetodo.dispatchEvent(new Event('change')); }
        """
        cap.evaluate(js_venta)
        time.sleep(1.0)
        cap.capture('06_punto_de_venta.png')

        # 7. Rol Dueño: Cierre de Caja
        print("7. Iniciando sesión como Dueño para Cierre de Caja...")
        cap.login('dueno_coagra')
        cap.navigate('http://127.0.0.1:8000/transaccional/cierre/nuevo/', wait_sec=2.5)
        cap.capture('07_cierre_caja.png')

        # 8. Historial de Cierres de Caja
        print("8. Capturando Historial de Cierres...")
        cap.navigate('http://127.0.0.1:8000/transaccional/cierres/', wait_sec=2.5)
        cap.capture('08_historial_cierres.png')

        # 9. Rol Contador: Módulo ETL - Carga de Estados
        print("9. Iniciando sesión como Contador (contador_coagra)...")
        cap.login('contador_coagra')
        cap.navigate('http://127.0.0.1:8000/etl/carga/', wait_sec=2.5)
        cap.capture('09_etl_carga.png')

        # 10. Módulo ETL: Matriz de Ratios Financieros
        print("10. Capturando Ratios Financieros...")
        cap.navigate('http://127.0.0.1:8000/etl/ratios/', wait_sec=2.5)
        cap.capture('10_etl_ratios.png')

        # 11. Módulo ETL: Historial de Cargas
        print("11. Capturando Historial de Cargas...")
        cap.navigate('http://127.0.0.1:8000/etl/historial/', wait_sec=2.5)
        cap.capture('11_etl_historial.png')

        print("\n¡TODAS LAS CAPTURAS FUERON TOMADAS EXITOSAMENTE!")
    finally:
        cap.close()

if __name__ == '__main__':
    main()
