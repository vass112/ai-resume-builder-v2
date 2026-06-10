import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

# Read the library GND symbol
with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/power.kicad_sym', 'r', encoding='utf-8') as f:
    lib_text = f.read()
start = lib_text.index('(symbol "GND"')
depth, i = 0, start
while i < len(lib_text):
    if lib_text[i] == '(': depth += 1
    elif lib_text[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
lib_gnd = lib_text[start:i+1]

# Read the working min.kicad_sch and replace ONLY the lib_symbols GND
with open('C:/Users/DELL/my-board/min.kicad_sch', 'r', encoding='utf-8') as f:
    min_content = f.read()

# Find lib_symbols section
ls_start = min_content.index('(lib_symbols')
depth, i = 0, ls_start
while i < len(min_content):
    if min_content[i] == '(': depth += 1
    elif min_content[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
ls_end = i + 1

old_ls = min_content[ls_start:ls_end]
new_ls = f'(lib_symbols\n{lib_gnd}\n)'

new_content = min_content[:ls_start] + new_ls + min_content[ls_end:]

# Also need to update instance lib_id reference
old_inst = '(lib_id "power:GND")'
new_inst = '(lib_id "GND")'
new_content = new_content.replace(old_inst, new_inst)

o = new_content.count('(')
c = new_content.count(')')
print(f'Balanced: {"OK" if o==c else "FAIL!"} ({o}/{c})')

path = 'C:/Users/DELL/my-board/test_lib_gnd_in_min.kicad_sch'
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, timeout=30)
if os.path.exists(rpt):
    with open(rpt, encoding='utf-8') as f:
        report = f.read()
    print(f'Test: OK (exit={result.returncode})')
    for l in report.split('\n')[:5]:
        print('  ' + l)
else:
    print(f'Test: FAIL (exit={result.returncode})')
    print(f'  stderr: {result.stderr.decode()}')
