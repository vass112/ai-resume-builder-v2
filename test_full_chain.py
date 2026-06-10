import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

def read_lib_sym(lib, name):
    with open(f'C:/Program Files/KiCad/8.0/share/kicad/symbols/{lib}.kicad_sym') as f:
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

def test(name, lib_syms, instances):
    o = lib_syms.count('(') + instances.count('(')
    c = lib_syms.count(')') + instances.count(')')
    # Actually count whole file
    header = f'(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n\t(uuid "{nu()}")\n\t(paper "A4")\n\t(title_block\n\t\t(title "Test")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n'
    footer = '\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n'
    sch = header + '\t(lib_symbols\n' + lib_syms + ')\n' + instances + footer
    o = sch.count('('); c = sch.count(')')
    if o != c:
        print(f'{name}: SKIP (unbalanced {o}/{c})')
        return False
    
    path = f'C:/Users/DELL/my-board/{name}.kicad_sch'
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
        print(f'{name}: OK ({errors} err, {warnings} warn)')
        return True
    else:
        print(f'{name}: FAIL (exit={result.returncode})')
        return False

# Hand-crafted single-instance helper
def inst(lib_id, ref, value, num_pins):
    pins = ''
    for pn in range(1, num_pins + 1):
        pins += f'\t\t(pin "{pn}"\n\t\t\t(uuid "{nu()}")\n\t\t)\n'
    return (f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "{nu()}")\n'
        f'\t\t(property "Reference" "{ref}" (at 50 56.35 0) (effects (font (size 1.27 1.27))))\n'
        f'\t\t(property "Value" "{value}" (at 50 43.65 0) (effects (font (size 1.27 1.27))))\n'
        f'\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        f'\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        f'{pins}'
        f'\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/{nu()}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')

# Test: GND + R + LED + ESP32 all together
all_libs = f'{gnd}\n{r}\n{led}\n{esp32}'
all_insts = inst('Device:R', 'R1', '220', 2) + inst('Device:LED', 'D1', 'LED', 2) + inst('power:GND', '#PWR1', 'GND', 1)
test('t_all', all_libs, all_insts)

# Test: GND only (from power.kicad_sym)
test('t_gnd', gnd, inst('power:GND', '#PWR1', 'GND', 1))

# Test: GND + R
test('t_gnd_r', f'{gnd}\n{r}', inst('power:GND', '#PWR1', 'GND', 1) + inst('Device:R', 'R1', '220', 2))

# Test: GND + R + LED
test('t_gnd_r_led', f'{gnd}\n{r}\n{led}', inst('power:GND', '#PWR1', 'GND', 1) + inst('Device:R', 'R1', '220', 2) + inst('Device:LED', 'D1', 'LED', 2))

# Test: GND + ESP32
test('t_gnd_esp32', f'{gnd}\n{esp32}', inst('power:GND', '#PWR1', 'GND', 1) + inst('MCU_Module:Arduino_Nano_ESP32', 'U1', 'Arduino Nano ESP32', 30))
