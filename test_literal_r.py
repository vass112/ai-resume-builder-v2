import uuid, subprocess, os

def nu(): return str(uuid.uuid4())

# Literal R symbol from Device library (with Device: prefix)
r_sym = '''\t(symbol "Device:R"
\t\t(pin_numbers hide)
\t\t(pin_names
\t\t\t(offset 0)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(property "Reference" "R"
\t\t\t(at 2.032 0 90)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "R"
\t\t\t(at 0 0 90)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at -1.778 0 90)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(symbol "Device:R_0_1"
\t\t\t(rectangle
\t\t\t\t(start -1.016 -2.54) (end 1.016 2.54)
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type none))
\t\t\t)
\t\t)
\t\t(symbol "Device:R_1_1"
\t\t\t(pin passive line
\t\t\t\t(at 0 3.81 270) (length 1.27)
\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))
\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 0 -3.81 90) (length 1.27)
\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))
\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))
\t\t\t)
\t\t)
\t)'''

# Construct minimal schematic with just R symbol + R1 instance
sch = '''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "''' + nu() + '''")
\t(paper "A4")
\t(title_block
\t\t(title "Test R Only")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
''' + r_sym + '''\n)
\t(symbol
\t\t(lib_id "Device:R")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "''' + nu() + '''")
\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "220" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "''' + nu() + '''"))
\t\t(pin "2" (uuid "''' + nu() + '''"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/''' + nu() + '''"
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

o = sch.count('('); c = sch.count(')')
print(f'Balanced: {"OK" if o==c else "FAIL"} ({o}/{c})')

path = 'C:/Users/DELL/my-board/test_literal_r.kicad_sch'
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
