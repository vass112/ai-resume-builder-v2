import re

min_data = open('C:/Users/DELL/my-board/test_lib_gnd_in_min.kicad_sch', 'rb').read()
ts1_data = open('C:/Users/DELL/my-board/ts1_gnd.kicad_sch', 'rb').read()

# Strip UUID-like patterns and compare
def normalize(text):
    text = re.sub(r'"[0-9a-f-]{36}"', 'UUID', text)
    text = re.sub(r'at [0-9 .-]+', 'at POS', text)
    text = re.sub(r'number "[0-9]+"', 'number N', text)
    text = re.sub(r'reference "[A-Za-z0-9#]+"', 'reference REF', text)
    text = re.sub(r'path "/[0-9a-f-]{36}"', 'path /PATH', text)
    text = re.sub(r'uuid "[0-9a-f-]{36}"', 'uuid UUID', text)
    text = re.sub(r'page "[0-9]+"', 'page N', text)
    text = re.sub(r'date "[^"]+"', 'date D', text)
    return text

min_norm = normalize(min_data.decode('utf-8'))
ts1_norm = normalize(ts1_data.decode('utf-8'))

# Compare line by line
min_lines = min_norm.split('\n')
ts1_lines = ts1_norm.split('\n')
diffs = []
for i in range(max(len(min_lines), len(ts1_lines))):
    m = min_lines[i] if i < len(min_lines) else '<EOF>'
    t = ts1_lines[i] if i < len(ts1_lines) else '<EOF>'
    if m != t:
        diffs.append((i, m, t))

print(f"Total diffs: {len(diffs)}")
for i, m, t in diffs[:20]:
    print(f'Line {i+1}:')
    print(f'  min: {repr(m)}')
    print(f'  ts1: {repr(t)}')
