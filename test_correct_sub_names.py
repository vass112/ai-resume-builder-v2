import subprocess

with open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch', 'r', encoding='utf-8') as f:
    tpl = f.read()

ls_start = tpl.index('(lib_symbols')
depth, i = 0, ls_start
while i < len(tpl):
    if tpl[i] == '(': depth += 1
    elif tpl[i] == ')':
        depth -= 1
        if depth == 0:
            ls_section = tpl[ls_start:i+1]
            break
    i += 1

def extract(name):
    idx = ls_section.index(f'(symbol "{name}"')
    depth, i = 0, idx
    while i < len(ls_section):
        if ls_section[i] == '(': depth += 1
        elif ls_section[i] == ')':
            depth -= 1
            if depth == 0:
                return ls_section[idx:i+1]
        i += 1

gnd_sym = extract('power:GND')

# CRITICAL TEST: Use GND body, but:
# - Main symbol: Device:R
# - Sub-symbols: R_0_1, R_1_1 (NOT Device:R_0_1, NOT GND_0_1!)
gnd_correct_body = gnd_sym

# Step 1: Change main symbol name
gnd_correct_body = gnd_correct_body.replace('(symbol "power:GND"', '(symbol "Device:R"')

# Step 2: Change sub-symbol names to match symbol name (R)
gnd_correct_body = gnd_correct_body.replace('"GND_', '"R_')

# Step 3: Update property values
gnd_correct_body = gnd_correct_body.replace('(property "Value" "GND"', '(property "Value" "R"')
gnd_correct_body = gnd_correct_body.replace('(property "Reference" "#PWR"', '(property "Reference" "R"')
gnd_correct_body = gnd_correct_body.replace('(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"', '(property "Description" "Resistor"')
gnd_correct_body = gnd_correct_body.replace('(property "ki_keywords" "power-flag"', '(property "ki_keywords" "resistor"')
gnd_correct_body = gnd_correct_body.replace('(name "GND"', '(name "~"')
gnd_correct_body = gnd_correct_body.replace('(property "Datasheet" ""', '(property "Datasheet" "~"')

def make_sch(sym_content, libid, val, name_suffix, pins='1'):
    pins_def = ''.join(f'\t\t(pin "{n}" (uuid "pin{n}"))\n' for n in pins.split(','))
    inst = f'''\t(symbol
\t\t(lib_id "{libid}")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "X1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "{val}" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
{pins_def}\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/"
\t\t\t\t\t(reference "X1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''
    sch = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test-uuid")
\t(paper "A4")
\t(title_block
\t\t(title "Test {name_suffix}")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{sym_content}
)
{inst}
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''
    path = f'C:/Users/DELL/my-board/test_{name_suffix}.kicad_sch'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sch)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
    return r.returncode == 0

# Test: Device:R with correct sub-symbol names (R_0_1, R_1_1)
ok = make_sch(gnd_correct_body, 'Device:R', 'R', 'dev_r_correct_sub', '1')
print(f'Device:R correct subs (R_0_1): {"OK" if ok else "FAIL"}')

# Test: power:R with correct sub-symbol names
power_r_body = gnd_sym.replace('(symbol "power:GND"', '(symbol "power:R"').replace('"GND_', '"R_')
power_r_body = power_r_body.replace('(property "Value" "GND"', '(property "Value" "R"')
power_r_body = power_r_body.replace('(property "Reference" "#PWR"', '(property "Reference" "R"')
power_r_body = power_r_body.replace('(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"', '(property "Description" "Resistor"')
power_r_body = power_r_body.replace('(property "ki_keywords" "power-flag"', '(property "ki_keywords" "resistor"')
power_r_body = power_r_body.replace('(name "GND"', '(name "~"')
ok = make_sch(power_r_body, 'power:R', 'R', 'power_r_correct_sub', '1')
print(f'power:R correct subs: {"OK" if ok else "FAIL"}')

# Test: X:Y correct subs
xy_body = gnd_sym.replace('(symbol "power:GND"', '(symbol "X:Y"').replace('"GND_', '"Y_')
xy_body = xy_body.replace('(property "Value" "GND"', '(property "Value" "Y"')
xy_body = xy_body.replace('(property "Reference" "#PWR"', '(property "Reference" "Y"')
xy_body = xy_body.replace('(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"', '(property "Description" "Test Y"')
xy_body = xy_body.replace('(property "ki_keywords" "power-flag"', '(property "ki_keywords" "test"')
xy_body = xy_body.replace('(name "GND"', '(name "~"')
ok = make_sch(xy_body, 'X:Y', 'Y', 'xy_correct_sub', '1')
print(f'X:Y correct subs: {"OK" if ok else "FAIL"}')
