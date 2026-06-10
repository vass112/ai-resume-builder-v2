import uuid, os, subprocess

nu = lambda: str(uuid.uuid4())
UID = nu()

tpl = open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch').read()
dev = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym').read()
mcu = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/MCU_Module.kicad_sym').read()

def find_matching(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    return text[start:]

def get_sym(text, name):
    return find_matching(text, text.index('(symbol "' + name + '"'))

gnd = get_sym(tpl, 'power:GND')

def make_sch(lib_syms, instances, path):
    sch = '(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n\t(uuid "' + nu() + '")\n\t(paper "A4")\n\t(title_block\n\t\t(title "Test")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n\t(lib_symbols\n'
    for name, sym in lib_syms:
        sch += sym + '\n'
    sch += ')\n'
    sch += instances
    sch += '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n)\n'
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
        print(f'{path}: ERC ran ({errors} err, {warnings} warn)')
        return True
    else:
        print(f'{path}: FAILED (exit={result.returncode})')
        return False

# Step 1: Just GND (like minimal but using template's GND symbol)
sch_ok = make_sch([('power:GND', gnd)], 
    '\t(symbol\n\t\t(lib_id "power:GND")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "#PWR1"\n\t\t\t(at 50 56.35 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Value" "GND"\n\t\t\t(at 50 53.81 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Footprint" ""\n\t\t\t(at 50 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at 50 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + UID + '"\n\t\t\t\t\t(reference "#PWR1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)',
    'C:/Users/DELL/my-board/step1.kicad_sch')

if not sch_ok: exit()

# Step 2: GND + R (from Device.kicad_sym)
r = get_sym(dev, 'R')
sch_ok = make_sch([('power:GND', gnd), ('Device:R', r)],
    # GND instance
    '\t(symbol\n\t\t(lib_id "power:GND")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "#PWR1"\n\t\t\t(at 50 56.35 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Value" "GND"\n\t\t\t(at 50 53.81 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Footprint" ""\n\t\t\t(at 50 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at 50 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + UID + '"\n\t\t\t\t\t(reference "#PWR1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'
    # R instance
    + '\t(symbol\n\t\t(lib_id "Device:R")\n\t\t(at 80 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "R1"\n\t\t\t(at 80 56.35 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Value" "220"\n\t\t\t(at 80 53.81 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"\n\t\t\t(at 80 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at 80 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n\t\t(pin "2"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + UID + '"\n\t\t\t\t\t(reference "R1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)',
    'C:/Users/DELL/my-board/step2.kicad_sch')

if not sch_ok: exit()

# Step 3: GND + R + LED (from Device.kicad_sym)
led = get_sym(dev, 'LED')
# Build the same as step2 but add LED
sch_ok = make_sch([('power:GND', gnd), ('Device:R', r), ('Device:LED', led)],
    open('C:/Users/DELL/my-board/step2.kicad_sch').read().split('(sheet_instances')[0] +
    '\t(symbol\n\t\t(lib_id "Device:LED")\n\t\t(at 120 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "D1"\n\t\t\t(at 120 56.35 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Value" "LED"\n\t\t\t(at 120 53.81 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Footprint" "LED_THT:LED_D5.0mm"\n\t\t\t(at 120 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at 120 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n\t\t(pin "2"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + UID + '"\n\t\t\t\t\t(reference "D1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)' +
    '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n)',
    'C:/Users/DELL/my-board/step3.kicad_sch')

if not sch_ok: exit()

# Step 4: GND + ESP32 (from MCU_Module)
esp32 = get_sym(mcu, 'Arduino_Nano_ESP32')

# Build ESP32 pins
esp_pins = ''
for pn in range(1, 31):
    esp_pins += '\t\t(pin "' + str(pn) + '"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n'

# Write step4
sch4 = '(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n\t(uuid "' + nu() + '")\n\t(paper "A4")\n\t(title_block\n\t\t(title "Test 4 - ESP32")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n\t(lib_symbols\n' + gnd + '\n' + esp32 + '\n)\n'
inst4 = '\t(symbol\n\t\t(lib_id "MCU_Module:Arduino_Nano_ESP32")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "U1"\n\t\t\t(at 50 56.35 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Value" "Arduino Nano ESP32"\n\t\t\t(at 50 43.65 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Footprint" "Module:Arduino_Nano"\n\t\t\t(at 50 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at 50 50 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n' + esp_pins + '\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + UID + '"\n\t\t\t\t\t(reference "U1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
inst4 += '\t(symbol\n\t\t(lib_id "power:GND")\n\t\t(at 50 80 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "#PWR1"\n\t\t\t(at 50 86.35 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Value" "GND"\n\t\t\t(at 50 83.81 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n\t\t(property "Footprint" ""\n\t\t\t(at 50 80 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at 50 80 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "' + nu() + '")\n\t\t)\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + UID + '"\n\t\t\t\t\t(reference "#PWR1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
inst4 += '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n)\n'

with open('C:/Users/DELL/my-board/step4.kicad_sch', 'w') as f:
    f.write(sch4 + inst4)

rpt = 'C:/Users/DELL/my-board/step4.rpt'
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, 'C:/Users/DELL/my-board/step4.kicad_sch'], capture_output=True, timeout=30)
if os.path.exists(rpt):
    with open(rpt) as f:
        report = f.read()
    errors = len([l for l in report.split('\n') if 'error' in l.lower()])
    warnings = len([l for l in report.split('\n') if 'warning' in l.lower()])
    print(f'step4 (GND+ESP32): ERC ran ({errors} err, {warnings} warn)')
else:
    print(f'step4 (GND+ESP32): FAILED (exit={result.returncode})')
