with open('moduloETL/etl_financiero.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
print('=== CANONICAL_ACCOUNTS ===')
for i, l in enumerate(lines[:180]):
    if 'CANONICAL' in l or 'MANDATORY' in l or 'REQUIRED' in l:
        for j in range(i, min(i+40, len(lines))):
            print(lines[j])
        break

print('\n=== _validate_and_sanitize ===')
for i, l in enumerate(lines):
    if 'def _validate_and_sanitize' in l:
        for j in range(i, min(i+90, len(lines))):
            print(lines[j])
        break

print('\n=== _compute_ml_features ===')
for i, l in enumerate(lines):
    if 'def _compute_ml_features' in l:
        for j in range(i, min(i+90, len(lines))):
            print(lines[j])
        break
