import subprocess

with open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch', 'r', encoding='utf-8') as f:
    tpl = f.read()

# Extract power:GND symbol
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

# The base instance - same as test_tpl_gnd_standalone
instance = '''\t(symbol
\t\t(lib_id "INSTANCE_LIBID")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "#PWR1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "VAL" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1-uuid1"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/path-uuid"
\t\t\t\t\t(reference "#PWR1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''

def make_sch(symbol_content, libid, value, path_suffix):
    sym = symbol_content
    inst = instance.replace('INSTANCE_LIBID', libid).replace('VAL', value)
    sch = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test-uuid")
\t(paper "A4")
\t(title_block
\t\t(title "Test {path_suffix}")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{sym}
)
{inst}
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''
    path = f'C:/Users/DELL/my-board/test_min_{path_suffix}.kicad_sch'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sch)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr

# Test A: EXACT template GND (should work, it's the control)
ok, err = make_sch(gnd_sym, 'power:GND', 'GND', 'ctrl')
print(f'A (exact template GND): {"OK" if ok else "FAIL"}')

# Test B: Only rename symbol and lib_id to Device:R, nothing else changed
r_sym = gnd_sym.replace('(symbol "power:GND"', '(symbol "Device:R"')
ok, err = make_sch(r_sym, 'Device:R', 'R', 'rename_r')
print(f'B (rename to Device:R): {"OK" if ok else "FAIL"}')

# Test C: rename but also replace sub-symbol names
r_sym2 = gnd_sym
r_sym2 = r_sym2.replace('(symbol "power:GND"', '(symbol "Device:R"')
r_sym2 = r_sym2.replace('"GND_', '"Device:R_')
ok, err = make_sch(r_sym2, 'Device:R', 'R', 'rename_r2')
print(f'C (rename + sub-symbol): {"OK" if ok else "FAIL"}')

# Test D: rename to power:R (same library prefix)
r_sym3 = gnd_sym.replace('(symbol "power:GND"', '(symbol "power:R"').replace('"GND_', '"power:R_')
ok, err = make_sch(r_sym3, 'power:R', 'R', 'rename_power')
print(f'D (rename to power:R): {"OK" if ok else "FAIL"}')

# Test E: rename to X:Y (nonsense prefix)
r_sym4 = gnd_sym.replace('(symbol "power:GND"', '(symbol "X:Y"').replace('"GND_', '"X:Y_')
ok, err = make_sch(r_sym4, 'X:Y', 'Y', 'rename_xy')
print(f'E (rename to X:Y): {"OK" if ok else "FAIL"}')

# Test F: Just name without colon
r_sym5 = gnd_sym.replace('(symbol "power:GND"', '(symbol "MYR"').replace('"GND_', '"MYR_')
ok, err = make_sch(r_sym5, 'MYR', 'R', 'rename_myr')
print(f'F (rename to MYR): {"OK" if ok else "FAIL"}')

# Test G: rename to Device:R but keep sub-symbol names as GND_*
r_sym6 = gnd_sym.replace('(symbol "power:GND"', '(symbol "Device:R"')
# Don't change GND_ sub-symbols
ok, err = make_sch(r_sym6, 'Device:R', 'R', 'rename_r_nosub')
print(f'G (Device:R, no sub rename): {"OK" if ok else "FAIL"}')
