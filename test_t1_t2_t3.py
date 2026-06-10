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

# Also extract the library R and remove its sub-symbol structure, use template structure
with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym', 'r', encoding='utf-8') as f:
    symlib = f.read()
idx = symlib.index('(symbol "R"\n')
depth, i = 0, idx
while i < len(symlib):
    if symlib[i] == '(': depth += 1
    elif symlib[i] == ')':
        depth -= 1
        if depth == 0:
            r_sym = symlib[idx:i+1]
            break
    i += 1

def write_and_test(content, name, path='C:/Users/DELL/my-board'):
    fpath = f'{path}/{name}.kicad_sch'
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', fpath.replace('.kicad_sch', '.rpt'), fpath], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr

# Test 1: GND with R's lib_id + name
# Take template GND but rename to Device:R
gnd_as_r = gnd_sym.replace('(symbol "power:GND"', '(symbol "Device:R"').replace('"GND_', '"Device:R_').replace('"GND"', '"Device:R"').replace('(property "Value" "GND"', '(property "Value" "R"').replace('(property "Reference" "#PWR"', '(property "Reference" "R"')
# Also rename the pin names
gnd_as_r = gnd_as_r.replace('(name "GND")', '(name "~")')
# Instance
sch1 = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test")
\t(paper "A4")
\t(title_block
\t\t(title "Test1")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{gnd_as_r}
)
\t(symbol
\t\t(lib_id "Device:R")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst1")
\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "R" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/"
\t\t\t\t\t(reference "R1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''
ok1, _ = write_and_test(sch1, 'test_t1_gnd_body_Device_R_name')
print(f't1 (GND body with Device:R name + lib_id): {"OK" if ok1 else "SKIP"}')

# Test 2: R symbol (library, unchanged) but with (lib_id "Device:R")
sch2 = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test")
\t(paper "A4")
\t(title_block
\t\t(title "Test2")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{r_sym}
)
\t(symbol
\t\t(lib_id "Device:R")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst1")
\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "220" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1"))
\t\t(pin "2" (uuid "pin2"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/"
\t\t\t\t\t(reference "R1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''
ok2, _ = write_and_test(sch2, 'test_t2_orig_R_Device_R_libid')
print(f't2 (orig R symbol, lib_id=Device:R, name=R): {"OK" if ok2 else "SKIP"}')

# Test 3: R symbol with full Device:R, but simplified sub-symbols (no rectangles) 
r_simple = r_sym.replace('(pin_numbers hide)\n', '')
# Remove rectangle
r_simple = r_simple.replace('\t\t\t\t(rectangle\n\t\t\t\t\t(start -1.016 -2.54) (end 1.016 2.54)\n\t\t\t\t\t(stroke (width 0.254) (type default))\n\t\t\t\t\t(fill (type none))\n\t\t\t\t)\n', '')
# Change name
r_simple = r_simple.replace('(symbol "R"\n', '(symbol "Device:R"\n').replace('"R_', '"Device:R_')
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    r_simple = r_simple.replace(f'(property "{p}" "R"', f'(property "{p}" "R"')  # Keep values as R, not Device:R

sch3 = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test")
\t(paper "A4")
\t(title_block
\t\t(title "Test3")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{r_simple}
)
\t(symbol
\t\t(lib_id "Device:R")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst1")
\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "220" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1"))
\t\t(pin "2" (uuid "pin2"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/"
\t\t\t\t\t(reference "R1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''
ok3, _ = write_and_test(sch3, 'test_t3_simple_R_Device_R')
print(f't3 (simplified R with Device:R name+lib_id): {"OK" if ok3 else "SKIP"}')
