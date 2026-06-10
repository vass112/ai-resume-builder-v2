import subprocess

# Extract power:GND from the power library
with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/power.kicad_sym', 'r', encoding='utf-8') as f:
    psym = f.read()

idx = psym.index('(symbol "GND"')
depth, i = 0, idx
while i < len(psym):
    if psym[i] == '(': depth += 1
    elif psym[i] == ')':
        depth -= 1
        if depth == 0:
            lib_gnd = psym[idx:i+1]
            break
    i += 1

# Make it power:GND prefix
lib_gnd_prefixed = lib_gnd.replace('(symbol "GND"', '(symbol "power:GND"').replace('"GND_', '"power:GND_')

# Get the template's power:GND for comparison
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
            tpl_gnd = ls_section[gnd_start:i+1]
            break
    i += 1

print("=== TEMPLATE power:GND ===")
print(tpl_gnd)
print()
print("=== LIBRARY power:GND (prefixed) ===")
print(lib_gnd_prefixed)
print()

# Write and test both
def make_sch(sym_content, libid, name):
    inst = f'''\t(symbol
\t\t(lib_id "{libid}")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "X1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "{name}" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1"))
\t\t(instances
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
\t\t(title "Test {name}")
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
    path = f'C:/Users/DELL/my-board/test_gnd_{name}.kicad_sch'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sch)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr

print("Template GND:", make_sch(tpl_gnd, 'power:GND', 'tpl_gnd')[0])
print("Library GND (prefixed):", make_sch(lib_gnd_prefixed, 'power:GND', 'lib_gnd')[0])
print("Library GND (unprefixed):", make_sch(lib_gnd, 'GND', 'lib_gnd_noprefix')[0])
