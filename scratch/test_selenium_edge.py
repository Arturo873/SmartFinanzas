import os, time
from selenium import webdriver
from selenium.webdriver.edge.options import Options

os.makedirs('docs/capturas', exist_ok=True)

options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1366,768')
options.add_argument('--disable-gpu')

print("Starting Edge WebDriver...")
driver = webdriver.Edge(options=options)
try:
    print("Navigating to login page...")
    driver.get('http://127.0.0.1:8000/login/')
    time.sleep(2)
    path = 'docs/capturas/01_login.png'
    driver.save_screenshot(path)
    print("Saved screenshot to:", path, "Size:", os.path.getsize(path))
finally:
    driver.quit()
