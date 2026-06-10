import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())
UID = nu()

# Test 1: Just GND + R + LED (no ESP32)
sch1 = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "{nu()}")
\t(paper "A4")
\t(title_block
\t\t(title "Test 1 - No ESP32")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
'''

# Read necessary lib symbols
tpl = open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch').read()
dev = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym').read()
mcu = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/MCU_Module.kicad_sym').read()

def find_matching(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0: return text[start:i+1]
        i += 1
    return text[start:]

def get_sym(text, name):
    return find_matching(text, text.index(f'(symbol "{name}"'))

gnd = get_sym(tpl, 'power:GND')
r = get_sym(dev, 'R')
led = get_sym(dev, 'LED')
esp32 = get_sym(mcu, 'Arduino_Nano_ESP32')

# Test 1: header + GND + R + LED
lib1 = f'\t(lib_symbols\n{gnd}\n{r}\n{led}\n)\n'
inst1 = f'''\t(symbol
\t\t(lib_id "power:GND")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{nu()}")
\t\t(property "Reference" "#PWR1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "GND" (at 50 53.81 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{nu()}"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/{UID}"
\t\t\t\t\t(reference "#PWR1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(symbol
\t\t(lib_id "Device:R")
\t\t(at 80 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{nu()}")
\t\t(property "Reference" "R1" (at 80 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "220" (at 80 53.81 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (at 80 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 80 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{nu()}"))
\t\t(pin "2" (uuid "{nu()}"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/{UID}"
\t\t\t\t\t(reference "R1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(symbol
\t\t(lib_id "Device:LED")
\t\t(at 120 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{nu()}")
\t\t(property "Reference" "D1" (at 120 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "LED" (at 120 53.81 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "LED_THT:LED_D5.0mm" (at 120 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 120 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{nu()}"))
\t\t(pin "2" (uuid "{nu()}"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/{UID}"
\t\t\t\t\t(reference "D1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)
'''

tests = {
    'test1_gnd_r_led': (lib1, inst1),
}

fp = 'C:/Users/DELL/my-board/test1.kicad_sch'
with open(fp, 'w') as f:
    f.write(sch1 + lib1 + inst1)

rpt = fp.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, fp], capture_output=True, text=True)
if os.path.exists(rpt):
    print('Test 1 (GND+R+LED): SUCCESS (ERC report generated)')
    with open(rpt) as f:
        print(f.read()[:300])
else:
    print(f'Test 1 (GND+R+LED): FAILED: {result.stderr or result.stdout}')

# Test 2: Add ESP32
sch2 = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "{nu()}")
\t(paper "A4")
\t(title_block
\t\t(title "Test 2 - With ESP32")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
'''

lib2 = f'\t(lib_symbols\n{gnd}\n{esp32}\n)\n'

inst2 = f'''\t(symbol
\t\t(lib_id "MCU_Module:Arduino_Nano_ESP32")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{nu()}")
\t\t(property "Reference" "U1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "Arduino Nano ESP32" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Module:Arduino_Nano" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
'''

# Add all 30 pins
for pn in range(1, 31):
    inst2 += f'\t\t(pin "{pn}" (uuid "{nu()}"))\n'

inst2 += f'''\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/{UID}"
\t\t\t\t\t(reference "U1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(symbol
\t\t(lib_id "power:GND")
\t\t(at 50 80 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{nu()}")
\t\t(property "Reference" "#PWR1" (at 50 86.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "GND" (at 50 83.81 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 80 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 80 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{nu()}"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/{UID}"
\t\t\t\t\t(reference "#PWR1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)
'''

fp = 'C:/Users/DELL/my-board/test2.kicad_sch'
with open(fp, 'w') as f:
    f.write(sch2 + lib2 + inst2)

rpt = fp.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, fp], capture_output=True, text=True)
if os.path.exists(rpt):
    print('Test 2 (ESP32+GND): SUCCESS (ERC report generated)')
    with open(rpt) as f:
        print(f.read()[:300])
else:
    print(f'Test 2 (ESP32+GND): FAILED: {result.stderr or result.stdout}')
