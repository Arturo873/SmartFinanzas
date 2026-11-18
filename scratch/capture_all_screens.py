import subprocess, time, urllib.request, json, os, base64
import websocket

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = os.path.abspath('scratch/edge_profile_full')
os.makedirs(user_data, exist_ok=True)
capturas_dir = os.path.abspath('docs/capturas')
os.makedirs(capturas_dir, exist_ok=True)

class ScreenCapturer:
    def __init__(self):
        self.proc = subprocess.Popen([
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
        with urllib.request.urlopen('http://127.0.0.1:9222/json') as resp:
            tabs = json.loads(resp.read().decode())
        page_tab = next((t for t in tabs if t.get('type') == 'page'), tabs[0])
        self.ws = websocket.create_connection(page_tab['webSocketDebuggerUrl'], timeout=15)
        self.msg_id = 0

    def send(self, method, params=None):
        self.msg_id += 1
        payload = {'id': self.msg_id, 'method': method}
        if params:
            payload['params'] = params
        self.ws.send(json.dumps(payload))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == self.msg_id:
                return m.get('result', {})

    def evaluate(self, js):
        return self.send('Runtime.evaluate', {'expression': js})

    def navigate(self, url, wait_s=2.5):
        self.send('Page.navigate', {'url': url})
        time.sleep(wait_s)

    def scroll(self, y):
        self.evaluate(f'window.scrollTo(0, {y});')
        time.sleep(0.8)

    def capture(self, filename):
        res = self.send('Page.captureScreenshot', {'format': 'png'})
        b64 = res['data']
        out_path = os.path.join(capturas_dir, filename)
        with open(out_path, 'wb') as f:
            f.write(base64.b64decode(b64))
        print(f" -> Guardado: {filename} ({os.path.getsize(out_path)} bytes)")
        return out_path

    def login(self, email, password='SmartFinanzas2026!'):
        self.navigate('http://127.0.0.1:8000/logout/', wait_s=1.0)
        self.navigate('http://127.0.0.1:8000/login/', wait_s=1.5)
        js = f"""
        document.querySelector('input[name="email"]').value = '{email}';
        document.querySelector('input[name="password"]').value = '{password}';
        document.querySelector('button[type="submit"], input[type="submit"]').click();
        """
        self.evaluate(js)
        time.sleep(3.5)

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()


def main():
    print("Iniciando sesión de captura automatizada...")
    cap = ScreenCapturer()
    try:
        # 1. Login
        print("\n1. Capturando Login...")
        cap.navigate('http://127.0.0.1:8000/login/', wait_s=2.0)
        cap.capture('01_login.png')

        # 2. Registro
        print("\n2. Capturando Registro...")
        cap.navigate('http://127.0.0.1:8000/registro/', wait_s=2.0)
        cap.capture('02_registro.png')

        # 3. Rol Dueño: Login y Dashboard General
        print("\n3. Login Dueño (dueno@coagra.cl) y Dashboard...")
        cap.login('dueno@coagra.cl')
        cap.navigate('http://127.0.0.1:8000/dashboard/', wait_s=3.5)
        cap.capture('03_dashboard_general.png')

        # 4. Dashboard SHAP y Variables Críticas (scroll leve)
        print("\n4. Capturando Explicabilidad SHAP...")
        cap.scroll(320)
        cap.capture('04_dashboard_shap.png')

        # 5. Dashboard Curva Temporal (scroll medio)
        print("\n5. Capturando Curva Temporal...")
        cap.scroll(750)
        cap.capture('05_dashboard_tendencia.png')

        # 6. Dashboard Recomendaciones
        print("\n6. Capturando Recomendaciones...")
        cap.scroll(1200)
        cap.capture('06_recomendaciones.png')

        # 7. Dashboard Predictivo a 90 días
        print("\n7. Capturando Dashboard Predictivo...")
        cap.navigate('http://127.0.0.1:8000/dashboard/predictivo/', wait_s=3.0)
        cap.capture('07_dashboard_predictivo.png')

        # 8. Cierre de Caja (Dueño)
        print("\n8. Capturando Cierre de Caja...")
        cap.navigate('http://127.0.0.1:8000/transaccional/cierre/nuevo/', wait_s=2.5)
        cap.capture('08_cierre_caja.png')

        # 9. Historial de Cierres (Dueño)
        print("\n9. Capturando Historial de Cierres...")
        cap.navigate('http://127.0.0.1:8000/transaccional/cierres/', wait_s=2.5)
        cap.capture('09_historial_cierres.png')

        # 10. Rol Trabajador: Punto de Venta
        print("\n10. Login Trabajador (trabajador@coagra.cl) y Punto de Venta...")
        cap.login('trabajador@coagra.cl')
        cap.navigate('http://127.0.0.1:8000/transaccional/ventas/nueva/', wait_s=2.5)
        js_demo_venta = """
        const inBruto = document.getElementById('id_gross_total');
        if (inBruto) { inBruto.value = '75000'; inBruto.dispatchEvent(new Event('input')); }
        const inDesc = document.getElementById('id_discount_amount');
        if (inDesc) { inDesc.value = '5000'; inDesc.dispatchEvent(new Event('input')); }
        const selMp = document.getElementById('id_payment_method');
        if (selMp && selMp.options.length > 1) { selMp.selectedIndex = 1; selMp.dispatchEvent(new Event('change')); }
        """
        cap.evaluate(js_demo_venta)
        time.sleep(1.2)
        cap.capture('10_punto_de_venta.png')

        # 11. Rol Contador: ETL Carga
        print("\n11. Login Contador (contador@coagra.cl) y ETL Carga...")
        cap.login('contador@coagra.cl')
        cap.navigate('http://127.0.0.1:8000/etl/carga/', wait_s=2.5)
        cap.capture('11_etl_carga.png')

        # 12. ETL Ratios Financieros
        print("\n12. Capturando Matriz de Ratios Financieros...")
        cap.navigate('http://127.0.0.1:8000/etl/ratios/', wait_s=2.5)
        cap.capture('12_etl_ratios.png')

        # 13. ETL Historial de Cargas
        print("\n13. Capturando Historial de Cargas...")
        cap.navigate('http://127.0.0.1:8000/etl/historial/', wait_s=2.5)
        cap.capture('13_etl_historial.png')

        print("\n¡PROCESO DE CAPTURA COMPLETADO CON ÉXITO TOTAL!")
    finally:
        cap.close()

if __name__ == '__main__':
    main()
