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

gnd_start = ls_section.index('(symbol "power:GND"')
depth, i = 0, gnd_start
while i < len(ls_section):
    if ls_section[i] == '(': depth += 1
    elif ls_section[i] == ')':
        depth -= 1
        if depth == 0:
            gnd_sym = ls_section[gnd_start:i+1]
            break
    i += 1

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

# Test: GND body with EVERYTHING changed to R (not just name)
gnd_full_r = gnd_sym.replace('power:GND', 'Device:R').replace('GND_', 'Device:R_')
# Change property values
gnd_full_r = gnd_full_r.replace('(property "Value" "GND"', '(property "Value" "R"')
gnd_full_r = gnd_full_r.replace('(property "Reference" "#PWR"', '(property "Reference" "R"')
gnd_full_r = gnd_full_r.replace('(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"', '(property "Description" "Resistor"')
gnd_full_r = gnd_full_r.replace('(property "ki_keywords" "power-flag"', '(property "ki_keywords" "resistor"')
# Change pin name from GND to ~
gnd_full_r = gnd_full_r.replace('(name "GND"', '(name "~"')
ok = make_sch(gnd_full_r, 'Device:R', 'R', 'gnd_full_r', '1')
print(f'GND body fully changed to R: {"OK" if ok else "FAIL"}')

# Test: GND body with EVERYTHING changed but name = power:R (original power prefix)
gnd_power_r = gnd_sym.replace('power:GND', 'power:R').replace('GND_', 'power:R_')
gnd_power_r = gnd_power_r.replace('(property "Value" "GND"', '(property "Value" "R"')
gnd_power_r = gnd_power_r.replace('(property "Reference" "#PWR"', '(property "Reference" "R"')
gnd_power_r = gnd_power_r.replace('(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"', '(property "Description" "Resistor"')
gnd_power_r = gnd_power_r.replace('(property "ki_keywords" "power-flag"', '(property "ki_keywords" "resistor"')
gnd_power_r = gnd_power_r.replace('(name "GND"', '(name "~"')
ok = make_sch(gnd_power_r, 'power:R', 'R', 'gnd_power_r', '1')
print(f'GND body fully changed to power:R: {"OK" if ok else "FAIL"}')

# What if I just leave the sub-symbol names as GND_* without changing them?
gnd_name_only = gnd_sym.replace('(symbol "power:GND"', '(symbol "Device:R"')
gnd_name_only = gnd_name_only.replace('(property "Value" "GND"', '(property "Value" "R"')
gnd_name_only = gnd_name_only.replace('(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"', '(property "Description" "Resistor"')
# Don't change sub-symbol names or property Reference
ok = make_sch(gnd_name_only, 'Device:R', 'R', 'gnd_name_only', '1')
print(f'GND body name+Value changed only: {"OK" if ok else "FAIL"}')
