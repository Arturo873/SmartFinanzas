import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

DAMODARAN_CTYPREM_URL = 'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html'
DAMODARAN_BETAS_URL = 'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html'
BCU_RATE_URL = 'https://si3.bcentral.cl/Siete/ES/Siete/Cuadro/CAP_DYB/MN_TASA_INTERES_09/TMS_16/T312'

DEFAULT_RF = 4.5
DEFAULT_ERP = 6.0

DEFAULT_SECTORES_BETA = {
    'Minería': 1.15,
    'Retail': 0.85,
    'Energía': 0.90,
    'Sector Bancario y Financiero': 1.05,
    'Telecomunicaciones': 0.75,
    'Agrícola y Forestal': 0.80,
    'Tecnología': 1.20,
    'Construcción e Inmobiliario': 1.10,
}

MAPEO_SECTORES = {
    'Minería': 'Metals & Mining',
    'Retail': 'Retail (General)',
    'Energía': 'Power',
    'Sector Bancario y Financiero': 'Banks (Regional)',
    'Telecomunicaciones': 'Telecom. Services',
    'Agrícola y Forestal': 'Farming/Agriculture',
    'Tecnología': 'Software (System & Application)',
    'Construcción e Inmobiliario': 'Engineering/Construction',
}

_cache = {}
CACHE_TTL = timedelta(hours=24)


def _get_cached(key):
    entry = _cache.get(key)
    if entry and datetime.now() - entry['time'] < CACHE_TTL:
        return entry['value']
    return None


def _set_cache(key, value):
    _cache[key] = {'value': value, 'time': datetime.now()}


def _normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def _fetch(url, timeout=15):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    resp = requests.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()
    return resp.text


def get_tasa_libre_riesgo():
    cached = _get_cached('tasa_libre_riesgo')
    if cached is not None:
        return cached, 'BCCh (BCU-10)'

    try:
        html = _fetch(BCU_RATE_URL)
        soup = BeautifulSoup(html, 'lxml')

        for row in soup.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            first = _normalize(cells[0].get_text(strip=True))
            second = _normalize(cells[1].get_text(strip=True)) if len(cells) > 1 else ''
            combined = (first + ' ' + second).strip()
            if '10 a' in combined and 'bono' in combined.lower() and 'uf' in combined.lower():
                values = []
                for cell in cells:
                    text = cell.get_text(strip=True).replace('%', '').replace('\xa0', '').strip()
                    if re.match(r'^-?\d+,\d+$', text):
                        values.append(float(text.replace(',', '.')))
                if values:
                    tasa = values[-1]
                    _set_cache('tasa_libre_riesgo', tasa)
                    return tasa, 'BCCh (BCU-10)'
    except Exception:
        pass

    return DEFAULT_RF, 'Valor por defecto'


def get_prima_riesgo_mercado():
    cached = _get_cached('prima_riesgo_mercado')
    if cached is not None:
        return cached, 'Damodaran (NYU)'

    try:
        html = _fetch(DAMODARAN_CTYPREM_URL)
        soup = BeautifulSoup(html, 'lxml')

        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 5 and _normalize(cells[0].get_text(strip=True)) == 'Chile':
                erp_text = cells[4].get_text(strip=True).replace('%', '').strip()
                erp = float(erp_text)
                _set_cache('prima_riesgo_mercado', erp)
                return erp, 'Damodaran (NYU)'
    except Exception:
        pass

    return DEFAULT_ERP, 'Valor por defecto'


def get_sectores_beta():
    cached = _get_cached('sectores_beta')
    if cached is not None:
        return cached, 'Damodaran (NYU)'

    try:
        html = _fetch(DAMODARAN_BETAS_URL)
        soup = BeautifulSoup(html, 'lxml')

        betas = {}
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            industry_name = _normalize(cells[0].get_text(strip=True))
            for our_sector, damodaran_name in MAPEO_SECTORES.items():
                if industry_name == damodaran_name:
                    try:
                        beta = float(cells[2].get_text(strip=True))
                        betas[our_sector] = beta
                    except ValueError:
                        pass
                    break

        if betas:
            _set_cache('sectores_beta', betas)
            return betas, 'Damodaran (NYU)'
    except Exception:
        pass

    return DEFAULT_SECTORES_BETA, 'Valor por defecto'
