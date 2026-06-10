import subprocess, os

# Take the working min.kicad_sch and replace GND with R symbol and instance
with open('C:/Users/DELL/my-board/min.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# Read the exact R symbol from Device.kicad_sym (unprefixed, as-is)
with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym', 'r', encoding='utf-8') as f:
    dev = f.read()

r_start = dev.index('(symbol "R"')
depth, i = 0, r_start
while i < len(dev):
    if dev[i] == '(': depth += 1
    elif dev[i] == ')':
        depth -= 1
        if depth == 0:
            r_sym = dev[r_start:i+1]
            break
    i += 1

# Replace lib_symbols section in min with JUST the R symbol
ls_start = sch.index('(lib_symbols')
depth, i = 0, ls_start
while i < len(sch):
    if sch[i] == '(': depth += 1
    elif sch[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break
    i += 1

# Construct: (lib_symbols\nR_SYM\n)
new_ls = f'(lib_symbols\n{r_sym}\n)'
sch = sch[:ls_start] + new_ls + sch[ls_end:]

# Replace the instance: change lib_id and pin references
# The instance section starts with (symbol after lib_symbols
inst_start = sch.index('\t(symbol')
# Get the first instance section
depth, i = 0, inst_start
while i < len(sch):
    if sch[i] == '(': depth += 1
    elif sch[i] == ')':
        depth -= 1
        if depth == 0:
            inst_end = i + 1
            break
    i += 1

old_inst = sch[inst_start:inst_end]

# Replace GND instance with R instance
# GND has: lib_id "power:GND", reference "#PWR1", value "GND", 1 pin
# R needs: lib_id "R", reference "R1", value "220", 2 pins
new_inst = '''\t(symbol
\t\t(lib_id "R")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "''' + sch.split('uuid "')[1].split('"')[0] + '''")
\t\t(property "Reference" "R1"
\t\t\t(at 50 56.35 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "220"
\t\t\t(at 50 43.65 0)
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
\t\t(pin "1" (uuid "11111111-1111-1111-1111-111111111111"))
\t\t(pin "2" (uuid "22222222-2222-2222-2222-222222222222"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/33333333-3333-3333-3333-333333333333"
\t\t\t\t\t(reference "R1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''

sch = sch[:inst_start] + new_inst + sch[inst_end:]

# Fix UUID extraction to avoid duplicates
import uuid
# Replace our placeholder UUIDs
sch = sch.replace('11111111-1111-1111-1111-111111111111', str(uuid.uuid4()))
sch = sch.replace('22222222-2222-2222-2222-222222222222', str(uuid.uuid4()))
sch = sch.replace('33333333-3333-3333-3333-333333333333', str(uuid.uuid4()))

o = sch.count('('); c = sch.count(')')
print(f'Balanced: {"OK" if o==c else "FAIL"} ({o}/{c})')

path = 'C:/Users/DELL/my-board/test_min_to_r.kicad_sch'
with open(path, 'w', encoding='utf-8') as f:
    f.write(sch)

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, text=True, timeout=30)
if os.path.exists(rpt):
    print(f'Test: OK (exit={result.returncode})')
else:
    print(f'Test: FAIL (exit={result.returncode}, stderr={result.stderr.strip()})')
