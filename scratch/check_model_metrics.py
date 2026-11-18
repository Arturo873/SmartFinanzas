import joblib
for p in ['capaAnalitica/modelo/metricas_v11.joblib', 'capaAnalitica/modelo/metricas.joblib', 'AppWeb/modelo_oficial/metricas_v11.joblib']:
    try:
        m = joblib.load(p)
        print('='*50)
        print(p)
        print('='*50)
        if isinstance(m, dict):
            for k, v in m.items():
                print(f'{k}: {v}')
        else:
            print(m)
    except Exception as e:
        print(f'Error loading {p}: {e}')
