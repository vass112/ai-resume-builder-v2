import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

dev = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym').read()

def find_matching(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    return text[start:]

def get_sym(text, name):
    return find_matching(text, text.index('(symbol "' + name + '"'))

r = get_sym(dev, 'R')

# Create schematic with ONLY the R symbol
sch = '(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n\t(uuid "' + nu() + '")\n\t(paper "A4")\n\t(title_block\n\t\t(title "Test R Only")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n\t(lib_symbols\n' + r + '\n)\n'
# No instances - just the lib definition and no symbol instances
# Actually we need instances too for ERC
sch += '\t(symbol\n\t\t(lib_id "Device:R")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))\n\t\t(property "Value" "220" (at 50 53.81 0) (effects (font (size 1.27 1.27))))\n\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t(pin "1" (uuid "' + nu() + '"))\n\t\t(pin "2" (uuid "' + nu() + '"))\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + nu() + '"\n\t\t\t\t\t(reference "R1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n'

path = 'C:/Users/DELL/my-board/test_r_only.kicad_sch'
with open(path, 'w') as f:
    f.write(sch)

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, timeout=30)
if os.path.exists(rpt):
    with open(rpt) as f:
        report = f.read()
    errors = len([l for l in report.split('\n') if 'error' in l.lower()])
    warnings = len([l for l in report.split('\n') if 'warning' in l.lower()])
    print('Test R Only: ERC ran (%d err, %d warn)' % (errors, warnings))
    print(report[:200])
else:
    print('Test R Only: FAILED (exit=%d)' % result.returncode)
    print('stderr:', result.stderr)
    print('stdout:', result.stdout)
