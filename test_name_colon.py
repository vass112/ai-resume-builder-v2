import subprocess

content = open('C:/Users/DELL/my-board/test_hand_r.kicad_sch', 'rb').read()
text = content.decode('utf-8')

# Test 1: Just add underscore to name
t1 = text.replace('(symbol "R"', '(symbol "XR"').replace('(symbol "R_', '(symbol "XR_').replace('(lib_id "R")', '(lib_id "XR")')
open('C:/Users/DELL/my-board/test_h_name1.kicad_sch', 'w', encoding='utf-8').write(t1)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', 'C:/Users/DELL/my-board/test_h_name1.rpt', 'C:/Users/DELL/my-board/test_h_name1.kicad_sch'], capture_output=True, text=True, timeout=30)
print(f'XR (no colon): exit={r.returncode}', 'OK' if r.returncode == 0 else 'FAIL')

# Test 2: Add colon without lib prefix
t2 = text.replace('"R"', '"X:R"').replace('"R_', '"X:R_').replace('(lib_id "R")', '(lib_id "X:R")')
open('C:/Users/DELL/my-board/test_h_name2.kicad_sch', 'w', encoding='utf-8').write(t2)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', 'C:/Users/DELL/my-board/test_h_name2.rpt', 'C:/Users/DELL/my-board/test_h_name2.kicad_sch'], capture_output=True, text=True, timeout=30)
print(f'X:R (with colon): exit={r.returncode}', 'OK' if r.returncode == 0 else 'FAIL')

# Test 3: Library colon prefix like Device:R
t3 = text.replace('(symbol "R"', '(symbol "Device:R"').replace('(symbol "R_', '(symbol "Device:R_').replace('(lib_id "R")', '(lib_id "Device:R")')
open('C:/Users/DELL/my-board/test_h_name3.kicad_sch', 'w', encoding='utf-8').write(t3)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', 'C:/Users/DELL/my-board/test_h_name3.rpt', 'C:/Users/DELL/my-board/test_h_name3.kicad_sch'], capture_output=True, text=True, timeout=30)
print(f'Device:R: exit={r.returncode}', 'OK' if r.returncode == 0 else 'FAIL')

# Test 4: Use the EXACT name from template (power:GND) but on R symbol
t4 = text.replace('(symbol "R"', '(symbol "power:R"').replace('(symbol "R_', '(symbol "power:R_').replace('(lib_id "R")', '(lib_id "power:R")')
open('C:/Users/DELL/my-board/test_h_name4.kicad_sch', 'w', encoding='utf-8').write(t4)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', 'C:/Users/DELL/my-board/test_h_name4.rpt', 'C:/Users/DELL/my-board/test_h_name4.kicad_sch'], capture_output=True, text=True, timeout=30)
print(f'power:R: exit={r.returncode}', 'OK' if r.returncode == 0 else 'FAIL')

# Test 5: Use exact template name power:GND on GND-like content, but change content to R
# Actually, let me just try Device:LED too
t5 = text.replace('(symbol "R"', '(symbol "Device:LED"').replace('(symbol "R_', '(symbol "Device:LED_').replace('(lib_id "R")', '(lib_id "Device:LED")')
open('C:/Users/DELL/my-board/test_h_name5.kicad_sch', 'w', encoding='utf-8').write(t5)
r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', 'C:/Users/DELL/my-board/test_h_name5.rpt', 'C:/Users/DELL/my-board/test_h_name5.kicad_sch'], capture_output=True, text=True, timeout=30)
print(f'Device:LED: exit={r.returncode}', 'OK' if r.returncode == 0 else 'FAIL')
