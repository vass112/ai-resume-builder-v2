import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

def read_lib_sym_raw(lib, name):
    with open(f'C:/Program Files/KiCad/8.0/share/kicad/symbols/{lib}.kicad_sym', 'rb') as f:
        text = f.read().decode('utf-8')
    start = text.index(f'(symbol "{name}"')
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                raw = text[start:i+1]
                return raw
        i += 1
    return text[start:]

# Get raw GND from power.kicad_sym
raw_gnd = read_lib_sym_raw('power', 'GND')
print('Raw GND length:', len(raw_gnd))
print('Raw GND balanced:', raw_gnd.count('('), raw_gnd.count(')'))
print()
print('First 300:')
print(raw_gnd[:300])
print()
print('Last 300:')
print(raw_gnd[-300:])

# Now embed it in a minimal schematic (same structure as working base)
sch = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "{nu()}")
\t(paper "A4")
\t(title_block
\t\t(title "Test")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{raw_gnd}
\t)
\t(symbol
\t\t(lib_id "power:GND")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{nu()}")
\t\t(property "Reference" "#PWR1"
\t\t\t(at 50 56.35 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "GND"
\t\t\t(at 50 53.81 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at 50 50 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at 50 50 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{nu()}")
\t\t)
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/{nu()}"
\t\t\t\t\t(reference "#PWR1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
'''

path = 'C:/Users/DELL/my-board/test_raw_gnd.kicad_sch'
with open(path, 'w') as f:
    f.write(sch)
print()
print('Full balanced:', sch.count('('), sch.count(')'))

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, timeout=30)
if os.path.exists(rpt):
    with open(rpt) as f:
        report = f.read()
    errors = len([l for l in report.split('\n') if 'error' in l.lower()])
    warnings = len([l for l in report.split('\n') if 'warning' in l.lower()])
    print(f'Test: OK ({errors} err, {warnings} warn)')
else:
    print(f'Test: FAIL (exit={result.returncode})')
