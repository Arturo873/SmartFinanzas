import zipfile, xml.etree.ElementTree as ET, os

pptx_files = [
    r'C:\Users\artur\Documents\RespaldoFeriaProyecto\MostrarFeria\SmartFinanzas_MVP_Arquitectura_Ingenieria_2026.pptx',
    r'C:\Users\artur\Documents\RespaldoFeriaProyecto\MostrarFeria\SmartFinanzas_Motor_Machine_Learning_2026.pptx',
    r'C:\Users\artur\Documents\RespaldoFeriaProyecto\MostrarFeria\Feria_Negocio_SmartFinanzas.pptx'
]

for p in pptx_files:
    print('='*70)
    print(os.path.basename(p))
    print('='*70)
    if not os.path.exists(p):
        print("No existe:", p)
        continue
    try:
        with zipfile.ZipFile(p, 'r') as z:
            slide_names = [n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            slide_names.sort(key=lambda x: int(''.join(filter(str.isdigit, x.split('/')[-1]))))
            for s in slide_names:
                tree = ET.fromstring(z.read(s))
                texts = [elem.text.strip() for elem in tree.iter() if elem.text and elem.text.strip()]
                full_text = ' '.join(texts).lower()
                keywords = ['latencia', 'tiempo', 'segundo', 'ms', '0.33', '1.58', '0.64', '0.08', 'sla', 'velocidad', 'rendimiento']
                if any(k in full_text for k in keywords):
                    print(f"\n--- {s} ---")
                    for t in texts:
                        if any(k in t.lower() for k in keywords + ['rf-', 'rnf-', 'kpi', 'sub-segundo', 'benchmark']):
                            print(f"  • {t}")
    except Exception as e:
        print('Error:', e)
