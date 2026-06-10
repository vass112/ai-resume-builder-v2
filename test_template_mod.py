import uuid, subprocess, os

def nu(): return str(uuid.uuid4())

with open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# Test 1: Just add a wire (no new symbols)
path1 = 'C:/Users/DELL/my-board/test_template_mod1.kicad_sch'
sch1 = sch.replace('(sheet_instances', f'\t(wire (pts (xy 73.66 71.12) (xy 93.66 81.12)) (stroke (width 0) (type solid)) (uuid "{nu()}"))\n\t(sheet_instances', 1)
with open(path1, 'w', encoding='utf-8') as f:
    f.write(sch1)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path1.replace('.kicad_sch', '.rpt'), path1], capture_output=True, text=True, timeout=30)
print(f'Test 1 (add wire only): exit={r.returncode}, {"OK" if r.returncode==0 else "FAIL"}')

# Test 2: Add a symbol to lib_symbols and an instance
# Read R symbol
with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym', 'r', encoding='utf-8') as f:
    dev_text = f.read()
r_start = dev_text.index('(symbol "R"')
depth, i = 0, r_start
while i < len(dev_text):
    if dev_text[i] == '(': depth += 1
    elif dev_text[i] == ')':
        depth -= 1
        if depth == 0:
            r_sym = dev_text[r_start:i+1]
            break
    i += 1

# Prefix the symbol name
r_sym = r_sym.replace('(symbol "R"', '(symbol "Device:R"').replace('(symbol "R_', '(symbol "Device:R_')

# Insert into lib_symbols
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

sch2 = sch[:ls_end-1] + '\n' + r_sym + '\n)' + sch[ls_end:]

# Add R1 instance
r_inst = f'\t(symbol\n\t\t(lib_id "Device:R")\n\t\t(at 93.66 81.12 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "{nu()}")\n\t\t(property "Reference" "R1"\n\t\t\t(at 93.66 93.66 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Value" "220"\n\t\t\t(at 93.66 87.51 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"\n\t\t\t(at 93.66 81.12 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at 93.66 81.12 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "{nu()}")\n\t\t)\n\t\t(pin "2"\n\t\t\t(uuid "{nu()}")\n\t\t)\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/{nu()}"\n\t\t\t\t\t(reference "R1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'

si_start = sch2.index('\t(sheet_instances')
sch2 = sch2[:si_start] + r_inst + sch2[si_start:]

o = sch2.count('('); c = sch2.count(')')
print(f'Test 2 balance: (={o}, )={c} {"OK" if o==c else "UNBALANCED!"}')

path2 = 'C:/Users/DELL/my-board/test_template_mod2.kicad_sch'
with open(path2, 'w', encoding='utf-8') as f:
    f.write(sch2)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path2.replace('.kicad_sch', '.rpt'), path2], capture_output=True, text=True, timeout=30)
print(f'Test 2 (add R symbol + R1 instance): exit={r.returncode}, {"OK" if r.returncode==0 else "FAIL"}')
if r.returncode != 0:
    print(f'  stderr: {r.stderr.strip()}')
