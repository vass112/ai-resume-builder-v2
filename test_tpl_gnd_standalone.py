import subprocess

with open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch', 'r', encoding='utf-8') as f:
    tpl = f.read()

# Extract the power:GND symbol from the template
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

# Put just this symbol in a minimal file
sch = f'''(kicad_sch
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
{gnd_sym}
)
\t(symbol
\t\t(lib_id "power:GND")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "#PWR1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "GND" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
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
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''

path = 'C:/Users/DELL/my-board/test_tpl_gnd_standalone.kicad_sch'
with open(path, 'w', encoding='utf-8') as f:
    f.write(sch)

r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
print(f'Template GND standalone: exit={r.returncode}', 'OK' if r.returncode == 0 else f'FAIL: {r.stderr.strip()}')
