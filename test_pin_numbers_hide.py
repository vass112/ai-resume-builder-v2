import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

def test(name, sym_content, instance):
    sch = (f'(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n'
           f'\t(uuid "{nu()}")\n\t(paper "A4")\n'
           f'\t(title_block\n\t\t(title "Test")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n'
           f'\t(lib_symbols\n{sym_content}\n)\n'
           f'{instance}'
           f'\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n')
    
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

def hand_sym(name, pin_numbers_hide=False, pin_names_hide=False):
    ph = '\t\t(pin_numbers hide)\n' if pin_numbers_hide else ''
    pnh = ' hide' if pin_names_hide else ''
    return (f'(symbol "{name}"\n'
            f'{ph}'
            f'\t\t(pin_names (offset 0){pnh})\n'
            f'\t\t(exclude_from_sim no)\n'
            f'\t\t(in_bom yes)\n'
            f'\t\t(on_board yes)\n'
            f'\t\t(property "Reference" "X" (at 0 0 0) (effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Value" "X" (at 0 0 0) (effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(symbol "X_0_1"\n'
            f'\t\t\t(rectangle (start -2.54 -2.54) (end 2.54 2.54)\n'
            f'\t\t\t\t(stroke (width 0.254) (type default))\n'
            f'\t\t\t\t(fill (type none))\n'
            f'\t\t\t)\n'
            f'\t\t)\n'
            f'\t\t(symbol "X_1_1"\n'
            f'\t\t\t(pin passive line\n'
            f'\t\t\t\t(at 0 2.54 270) (length 2.54)\n'
            f'\t\t\t\t(name "1" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t)\n'
            f'\t\t)\n'
            f'\t)')

def hand_inst(lib_id, ref, value):
    return (f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n'
            f'\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "{nu()}")\n'
            f'\t\t(property "Reference" "{ref}" (at 50 56.35 0) (effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Value" "{value}" (at 50 43.65 0) (effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(pin "1" (uuid "{nu()}"))\n'
            f'\t\t(instances\n'
            f'\t\t\t(project "t"\n'
            f'\t\t\t\t(path "/{nu()}"\n'
            f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')

# Test 1: Normal symbol (no pin_numbers hide, no pin_names hide)
s1 = hand_sym('TEST')
test('t1_normal', s1, hand_inst('Device:TEST', 'X1', 'TEST'))

# Test 2: With pin_numbers hide
s2 = hand_sym('TEST', pin_numbers_hide=True)
test('t2_pin_num_hide', s2, hand_inst('Device:TEST', 'X1', 'TEST'))

# Test 3: With pin_names hide
s3 = hand_sym('TEST', pin_names_hide=True)
test('t3_pin_name_hide', s3, hand_inst('Device:TEST', 'X1', 'TEST'))

# Test 4: Both
s4 = hand_sym('TEST', pin_numbers_hide=True, pin_names_hide=True)
test('t4_both', s4, hand_inst('Device:TEST', 'X1', 'TEST'))
