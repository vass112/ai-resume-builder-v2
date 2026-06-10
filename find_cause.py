import uuid, subprocess, os, sys

nu = lambda: str(uuid.uuid4())

def test(name, lib_syms, instances=''):
    # Create minimal schematic with given lib_syms and instances
    sch = '(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n\t(uuid "' + nu() + '")\n\t(paper "A4")\n\t(title_block\n\t\t(title "Test")\n\t\t(date "2026-06-07")\n\t\t(rev "1.0")\n\t)\n'
    if lib_syms:
        sch += '\t(lib_symbols\n'
        for sym in lib_syms:
            sch += sym + '\n'
        sch += ')\n'
    sch += instances
    sch += '\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n'
    
    o = sch.count('(')
    c = sch.count(')')
    if o != c:
        print('%s: UNBALANCED (%d/%d) - SKIPPING' % (name, o, c))
        return False
    
    path = 'C:/Users/DELL/my-board/' + name + '.kicad_sch'
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
        print('%s: OK (%d err, %d warn)' % (name, errors, warnings))
        return True
    else:
        print('%s: FAIL (exit=%d)' % (name, result.returncode))
        return False

# Working minimal GND symbol
gnd_hand = '''(symbol "power:GND"
\t\t\t(power)
\t\t\t(pin_names (offset 0))
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t\t(property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t\t(symbol "GND_0_1"
\t\t\t\t(polyline
\t\t\t\t\t(pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))
\t\t\t\t\t(stroke (width 0) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)
\t\t\t)
\t\t\t(symbol "GND_1_1"
\t\t\t\t(pin power_in line
\t\t\t\t\t(at 0 0 270)
\t\t\t\t\t(length 0) hide
\t\t\t\t\t(name "GND" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))
\t\t\t\t)
\t\t\t)
\t\t)'''

# Minimal GND instance
gnd_inst = '\t(symbol\n\t\t(lib_id "power:GND")\n\t\t(at 50 50 0)\n\t\t(unit 1)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "' + nu() + '")\n\t\t(property "Reference" "#PWR1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))\n\t\t(property "Value" "GND" (at 50 53.81 0) (effects (font (size 1.27 1.27))))\n\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t(pin "1" (uuid "' + nu() + '"))\n\t\t(instances\n\t\t\t(project "test"\n\t\t\t\t(path "/' + nu() + '"\n\t\t\t\t\t(reference "#PWR1")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'

# Test empty lib symbols (just header + sheet_instances)
test('empty', [])

# Test GND lib only, no instances
test('gnd_lib_only', [gnd_hand])

# Test GND lib with instance
test('gnd_lib_inst', [gnd_hand], gnd_inst)

# Now test adding R symbol from Device.kicad_sym
dev = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym').read()
def find_matching(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0: return text[start:i+1]
        i += 1
    return text[start:]
r_sym = find_matching(dev, dev.index('(symbol "R"'))

# Test GND lib + R lib, no instances
test('gnd_r_lib', [gnd_hand, r_sym])

# Test GND lib + R lib, only GND instance
r_lib_inst = gnd_inst  # same GND instance
test('gnd_r_lib_gnd_inst', [gnd_hand, r_sym], gnd_inst)
