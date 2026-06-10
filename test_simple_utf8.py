import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

def read_lib_sym(lib, name):
    with open(f'C:/Program Files/KiCad/8.0/share/kicad/symbols/{lib}.kicad_sym', 'r', encoding='utf-8') as f:
        text = f.read()
    start = text.index(f'(symbol "{name}"')
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    return text[start:]

gnd = read_lib_sym('power', 'GND')
r = read_lib_sym('Device', 'R')
led = read_lib_sym('Device', 'LED')
esp32 = read_lib_sym('MCU_Module', 'Arduino_Nano_ESP32')

def test(name, syms, insts):
    sch = f'(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n\t(uuid "{nu()}")\n\t(paper "A4")\n\t(title_block\n\t\t(title "Test")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n\t(lib_symbols\n{syms}\n)\n{insts}\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n'
    o = sch.count('('); c = sch.count(')')
    if o != c:
        print(f'{name}: SKIP (unbalanced {o}/{c})')
        return False
    path = f'C:/Users/DELL/my-board/{name}.kicad_sch'
    with open(path, 'w', encoding='utf-8') as f:
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
        print(f'{name}: OK ({errors} err, {warnings} warn)')
        return True
    else:
        print(f'{name}: FAIL (exit={result.returncode})')
        return False

def inst(lib_id, ref, value, num_pins, x=50, y=50):
    pins = ''
    for pn in range(1, num_pins + 1):
        pins += f'\t\t(pin "{pn}"\n\t\t\t(uuid "{nu()}")\n\t\t)\n'
    return (f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {x} {y} 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "{nu()}")\n'
        f'\t\t(property "Reference" "{ref}"\n\t\t\t(at {x} {round(y+6.35,2)} 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
        f'\t\t(property "Value" "{value}"\n\t\t\t(at {x} {round(y-6.35,2)} 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
        f'{pins}'
        f'\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/{nu()}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')

# 1. GND only (from power library)
test('ts1_gnd', gnd, inst('power:GND', '#PWR1', 'GND', 1))

# 2. R only (from Device)
test('ts2_r', r, inst('Device:R', 'R1', '220', 2))

# 3. LED only
test('ts3_led', led, inst('Device:LED', 'D1', 'LED', 2))

# 4. ESP32 only
test('ts4_esp32', esp32, inst('MCU_Module:Arduino_Nano_ESP32', 'U1', 'Arduino Nano ESP32', 30, 100, 100))

# 5. GND + R
test('ts5_gnd_r', f'{gnd}\n{r}', inst('power:GND', '#PWR1', 'GND', 1) + inst('Device:R', 'R1', '220', 2))
