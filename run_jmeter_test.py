import os
import shutil
import urllib.request
import urllib.parse
import http.cookiejar
import subprocess
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Obtain a fresh session from Django login
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("[1/5] Conectando a Django en http://127.0.0.1:8000/login/...")
resp = opener.open('http://127.0.0.1:8000/login/')
csrf = None
for c in cj:
    if c.name == 'csrftoken':
        csrf = c.value

data = urllib.parse.urlencode({'email': 'test1@test.cl', 'password': 'test123', 'csrfmiddlewaretoken': csrf}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/login/', data=data, headers={'Referer': 'http://127.0.0.1:8000/login/'})
resp = opener.open(req)

sessionid = None
for c in cj:
    if c.name == 'sessionid':
        sessionid = c.value

print(f"      Autenticación exitosa. SessionID: {sessionid}")

# 2. Prepare JMX Test Plan
jmx_path = os.path.join(BASE_DIR, "SmartFinanzas_ConcurrencyTest.jmx")
jtl_path = os.path.join(BASE_DIR, "jmeter_results.jtl")
html_report_dir = os.path.join(BASE_DIR, "jmeter_report_html")

if os.path.exists(jtl_path):
    os.remove(jtl_path)
if os.path.exists(html_report_dir):
    shutil.rmtree(html_report_dir)

jmx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="SmartFinanzas - Prueba de Rendimiento y Concurrencia" enabled="true">
      <stringProp name="TestPlan.comments">Prueba de Concurrencia con 20 usuarios concurrentes</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="Variables de Usuario" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="20 Usuarios Concurrentes (Dueño / Analista)" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">5</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">20</stringProp>
        <stringProp name="ThreadGroup.ramp_time">2</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">127.0.0.1</stringProp>
          <stringProp name="HTTPSampler.port">8000</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding">utf-8</stringProp>
          <stringProp name="HTTPSampler.path"></stringProp>
          <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
          <stringProp name="HTTPSampler.connect_timeout">10000</stringProp>
          <stringProp name="HTTPSampler.response_timeout">15000</stringProp>
        </ConfigTestElement>
        <hashTree/>
        <CookieManager guiclass="CookiePanel" testclass="CookieManager" testname="HTTP Cookie Manager" enabled="true">
          <collectionProp name="CookieManager.cookies">
            <elementProp name="sessionid" elementType="Cookie" testname="sessionid">
              <stringProp name="Cookie.value">{sessionid}</stringProp>
              <stringProp name="Cookie.domain">127.0.0.1</stringProp>
              <stringProp name="Cookie.path">/</stringProp>
              <boolProp name="Cookie.secure">false</boolProp>
              <longProp name="Cookie.expires">0</longProp>
              <boolProp name="Cookie.path_specified">true</boolProp>
              <boolProp name="Cookie.domain_specified">true</boolProp>
            </elementProp>
          </collectionProp>
          <boolProp name="CookieManager.clearEachIteration">false</boolProp>
          <boolProp name="CookieManager.controlledByThreadGroup">false</boolProp>
        </CookieManager>
        <hashTree/>
        <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">
          <collectionProp name="HeaderManager.headers">
            <elementProp name="" elementType="Header">
              <stringProp name="Header.name">User-Agent</stringProp>
              <stringProp name="Header.value">Apache-JMeter/5.6.3 (Windows NT 10.0)</stringProp>
            </elementProp>
            <elementProp name="" elementType="Header">
              <stringProp name="Header.name">Accept</stringProp>
              <stringProp name="Header.value">text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8</stringProp>
            </elementProp>
          </collectionProp>
        </HeaderManager>
        <hashTree/>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET /dashboard/ (Dashboard Gerencial)" enabled="true">
          <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/dashboard/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">false</boolProp>
          <boolProp name="HTTPSampler.image_parser">false</boolProp>
          <boolProp name="HTTPSampler.concurrentDwn">false</boolProp>
          <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
          <boolProp name="HTTPSampler.md5">false</boolProp>
          <intProp name="HTTPSampler.ipSourceType">0</intProp>
        </HTTPSamplerProxy>
        <hashTree/>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET /dashboard/predictivo/ (Inferencia ML &amp; SHAP)" enabled="true">
          <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/dashboard/predictivo/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">false</boolProp>
          <boolProp name="HTTPSampler.image_parser">false</boolProp>
          <boolProp name="HTTPSampler.concurrentDwn">false</boolProp>
          <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
          <boolProp name="HTTPSampler.md5">false</boolProp>
          <intProp name="HTTPSampler.ipSourceType">0</intProp>
        </HTTPSamplerProxy>
        <hashTree/>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET / (Landing Institucional)" enabled="true">
          <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">false</boolProp>
          <boolProp name="HTTPSampler.image_parser">false</boolProp>
          <boolProp name="HTTPSampler.concurrentDwn">false</boolProp>
          <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
          <boolProp name="HTTPSampler.md5">false</boolProp>
          <intProp name="HTTPSampler.ipSourceType">0</intProp>
        </HTTPSamplerProxy>
        <hashTree/>
        <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="Summary Report" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename">{jtl_path}</stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""

with open(jmx_path, "w", encoding="utf-8") as f:
    f.write(jmx_content)

print(f"[2/5] Plan de pruebas JMX generado en {jmx_path}")

# 3. Execute JMeter in non-GUI mode with HTML dashboard generation
jmeter_bat = os.path.join(BASE_DIR, "apache-jmeter-5.6.3", "bin", "jmeter.bat")
java_home = r"C:\Program Files\Eclipse Adoptium\jre-17.0.21.9-hotspot"

env = os.environ.copy()
env["JAVA_HOME"] = java_home
env["PATH"] = os.path.join(java_home, "bin") + os.pathsep + env.get("PATH", "")

cmd = [
    jmeter_bat,
    "-n",
    "-t", jmx_path,
    "-l", jtl_path,
    "-e",
    "-o", html_report_dir
]

print("[3/5] Ejecutando JMeter con 20 hilos concurrentes...")
proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
print("--- Salida JMeter ---")
print(proc.stdout)
if proc.stderr:
    print("--- Errores/Advertencias JMeter ---")
    print(proc.stderr)

# 4. Parse JTL and compute Summary Report stats
print("[4/5] Analizando métricas de rendimiento...")
samples = []
with open(jtl_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        samples.append(row)

by_label = {}
for s in samples:
    lbl = s["label"]
    if lbl not in by_label:
        by_label[lbl] = []
    by_label[lbl].append(s)

print("\n" + "="*80)
print("                          JMeter SUMMARY REPORT")
print("="*80)
header = f"{'Label':<42} | {'# Samples':>9} | {'Average (ms)':>12} | {'Min (ms)':>8} | {'Max (ms)':>8} | {'Error %':>8}"
print(header)
print("-" * len(header))

all_elapsed = []
all_errors = 0

for lbl, rows in by_label.items():
    count = len(rows)
    times = [int(r["elapsed"]) for r in rows]
    errors = sum(1 for r in rows if r["success"].lower() != "true")
    avg = sum(times) / count
    mn = min(times)
    mx = max(times)
    err_pct = (errors / count) * 100
    all_elapsed.extend(times)
    all_errors += errors
    print(f"{lbl:<42} | {count:>9} | {avg:>12.2f} | {mn:>8} | {mx:>8} | {err_pct:>7.2f}%")

total_count = len(all_elapsed)
total_avg = sum(all_elapsed) / total_count if total_count else 0
total_min = min(all_elapsed) if all_elapsed else 0
total_max = max(all_elapsed) if all_elapsed else 0
total_err_pct = (all_errors / total_count) * 100 if total_count else 0

print("-" * len(header))
print(f"{'TOTAL':<42} | {total_count:>9} | {total_avg:>12.2f} | {total_min:>8} | {total_max:>8} | {total_err_pct:>7.2f}%")
print("="*80)
print(f"Reporte HTML generado en: {html_report_dir}\\index.html")
