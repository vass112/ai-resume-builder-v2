import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

# Hand-crafted R symbol (minimal, just the shape)
r_hand = '''(symbol "R"
\t\t(pin_names (offset 0))
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(property "Reference" "R" (at 0 0 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "R" (at 0 0 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(symbol "R_0_1"
\t\t\t(rectangle
\t\t\t\t(start -1.016 -2.54) (end 1.016 2.54)
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type none))
\t\t\t)
\t\t)
\t\t(symbol "R_1_1"
\t\t\t(pin passive line
\t\t\t\t(at 0 3.81 270)
\t\t\t\t(length 1.27)
\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))
\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))
\t\t\t)
\t\t)
\t\t(symbol "R_2_1"
\t\t\t(pin passive line
\t\t\t\t(at 0 -3.81 90)
\t\t\t\t(length 1.27)
\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))
\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))
\t\t\t)
\t\t)
\t)'''

# Create schematic with hand-crafted R symbol
sch = '(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n\t(uuid "' + nu() + '")\n\t(paper "A4")\n\t(title_block\n\t\t(title "Test R Handcraft")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n\t(lib_symbols\n' + r_hand + '\n)\n'
sch += '\t(symbol\n\t\t(lib_id "Device:R")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))\n\t\t(property "Value" "220" (at 50 53.81 0) (effects (font (size 1.27 1.27))))\n\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t(pin "1" (uuid "' + nu() + '"))\n\t\t(pin "2" (uuid "' + nu() + '"))\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + nu() + '"\n\t\t\t\t\t(reference "R1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n'

path = 'C:/Users/DELL/my-board/test_r_hand.kicad_sch'
with open(path, 'w') as f:
    f.write(sch)

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, timeout=30)
if os.path.exists(rpt):
    with open(rpt) as f:
        report = f.read()
    errors = len([l for l in report.split('\n') if 'error' in l.lower()])
    warnings = len([l for l in report.split('\n') if 'warning' in l.lower()])
    print('Test R Handcraft: ERC ran (%d err, %d warn)' % (errors, warnings))
    print(report[:300])
else:
    print('Test R Handcraft: FAILED (exit=%d)' % result.returncode)
