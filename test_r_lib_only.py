import uuid, subprocess, os, re, sys

nu = lambda: str(uuid.uuid4())

# Use the EXACT working minimal file as base
min_content = open('C:/Users/DELL/my-board/min.kicad_sch').read()

# Test 1: Take working minimal, add R lib symbol (from Device) but no R instance
dev = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym').read()
def find_matching(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0: return text[start:i+1]
        i += 1
    return text[start:]
r_sym = find_matching(dev, dev.index('(symbol "R"'))

# Add R symbol after GND in lib_symbols
ls_end = min_content.find(')', min_content.find('(lib_symbols'))
ls_start = min_content.find('(lib_symbols')
depth = 0
for i in range(ls_start+len('(lib_symbols'), len(min_content)):
    if min_content[i] == '(': depth += 1
    elif min_content[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break

# Insert R symbol before closing of lib_symbols
new_content = min_content[:ls_end-1] + '\n' + r_sym + '\n' + min_content[ls_end-1:]

path = 'C:/Users/DELL/my-board/test_r_lib.kicad_sch'
with open(path, 'w') as f:
    f.write(new_content)

# Verify balance
o = new_content.count('(')
c = new_content.count(')')
print('Test R lib only: balanced' if o == c else 'UNBALANCED (%d / %d)' % (o, c))

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, timeout=30)
if os.path.exists(rpt):
    with open(rpt) as f:
        report = f.read()
    errors = len([l for l in report.split('\n') if 'error' in l.lower()])
    warnings = len([l for l in report.split('\n') if 'warning' in l.lower()])
    print('Test R lib only: ERC ran (%d err, %d warn)' % (errors, warnings))
else:
    print('Test R lib only: FAILED (exit=%d)' % result.returncode)
