import subprocess

# Take the template's working power:GND symbol and rename it
with open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch', 'rb') as f:
    tpl = f.read()

text = tpl.decode('utf-8')

# Find power:GND in lib_symbols
ls_start = text.index('(lib_symbols')
ls_end = 0
depth = 0
for i in range(ls_start, len(text)):
    if text[i] == '(': depth += 1
    elif text[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break

ls_section = text[ls_start:ls_end]

# Find the power:GND symbol in lib_symbols
gnd_start = ls_section.index('(symbol "power:GND"')
depth = 0
gnd_end = 0
for i in range(gnd_start, len(ls_section)):
    if ls_section[i] == '(': depth += 1
    elif ls_section[i] == ')':
        depth -= 1
        if depth == 0:
            gnd_end = i + 1
            break

gnd_sym = ls_section[gnd_start:gnd_end]

# Replace GND symbol with a renamed version (same structure, different name)
r_sym = gnd_sym.replace('(symbol "power:GND"', '(symbol "Device:R"').replace('"GND_', '"Device:R_').replace('"GND"', '"Device:R"').replace('name "GND"', 'name "~"').replace('(property "Value" "GND"', '(property "Value" "R"').replace('(property "Reference" "#PWR"', '(property "Reference" "R"')

# Create a minimal schematic with JUST this renamed symbol
min_sch = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test-uuid")
\t(paper "A4")
\t(title_block
\t\t(title "Test")
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
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "220" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1-uuid1"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/path-uuid"
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

path = 'C:/Users/DELL/my-board/test_template_gnd_as_r.kicad_sch'
with open(path, 'w', encoding='utf-8') as f:
    f.write(min_sch)

r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
print(f'Template GND-as-R symbol: exit={r.returncode}', 'OK' if r.returncode == 0 else f'FAIL: {r.stderr.strip()}')
