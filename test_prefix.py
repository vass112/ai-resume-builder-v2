import subprocess

content = open('C:/Users/DELL/my-board/test_hand_r.kicad_sch', 'rb').read()
text = content.decode('utf-8')
# Change symbol name from R to Device:R
text = text.replace('(symbol "R"', '(symbol "Device:R"')
text = text.replace('(symbol "R_', '(symbol "Device:R_')
text = text.replace('(lib_id "R")', '(lib_id "Device:R")')

o = text.count('('); c = text.count(')')
print(f'Balanced: {"OK" if o==c else "FAIL"} ({o}/{c})')

open('C:/Users/DELL/my-board/test_hand_r_prefixed.kicad_sch', 'w', encoding='utf-8').write(text)

r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', 'C:/Users/DELL/my-board/test_hand_r_prefixed.rpt', 'C:/Users/DELL/my-board/test_hand_r_prefixed.kicad_sch'], capture_output=True, text=True, timeout=30)
print(f'Prefixed name: exit={r.returncode}')
if r.returncode == 0:
    print('OK!')
else:
    print(f'FAIL: {r.stderr.strip()}')

# Also check if adding the Description property breaks it
text2 = content.decode('utf-8')
# Just add Description property
text2 = text2.replace('(property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
    '(property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t\t(property "Description" "Resistor" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
open('C:/Users/DELL/my-board/test_hand_r_desc.kicad_sch', 'w', encoding='utf-8').write(text2)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', 'C:/Users/DELL/my-board/test_hand_r_desc.rpt', 'C:/Users/DELL/my-board/test_hand_r_desc.kicad_sch'], capture_output=True, text=True, timeout=30)
print(f'Added Description: exit={r.returncode}')
if r.returncode == 0:
    print('OK!')
else:
    print(f'FAIL: {r.stderr.strip()}')
