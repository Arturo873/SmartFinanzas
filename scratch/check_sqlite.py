import sqlite3

for db in ['db.sqlite3', 'test.sqlite3']:
    print('===', db, '===')
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('Tables count:', len(tables))
        table_names = [t[0] for t in tables]
        for t in ['user', 'role', 'company', 'financial_ratio', 'financial_upload', 'risk_prediction', 'sale', 'payment_method']:
            if t in table_names:
                cursor.execute(f"SELECT count(*) FROM {t}")
                cnt = cursor.fetchone()[0]
                print(f"  {t}: {cnt} rows")
        conn.close()
    except Exception as e:
        print('Error:', e)
