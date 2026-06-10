import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

def test(name, sch_text):
    path = f'C:/Users/DELL/my-board/{name}.kicad_sch'
    with open(path, 'w') as f:
        f.write(sch_text)
    rpt = path.replace('.kicad_sch', '.rpt')
    try: os.remove(rpt)
    except: pass
    result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, timeout=30)
    if os.path.exists(rpt):
        print(f'{name}: OK')
        return True
    else:
        print(f'{name}: FAIL (exit={result.returncode})')
        return False

uid = nu()
proj_id = nu()

# Start with the EXACT working minimal schematic
base = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "{uid}")
\t(paper "A4")
\t(title_block
\t\t(title "Minimal Test")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
\t\t(symbol "power:GND"
\t\t\t(power)
\t\t\t(pin_names (offset 0))
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(property "Reference" "#PWR"
\t\t\t\t(at 0 -6.35 0)
\t\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t\t)
\t\t\t(property "Value" "GND"
\t\t\t\t(at 0 -3.81 0)
\t\t\t\t(effects (font (size 1.27 1.27)))
\t\t\t)
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
\t\t)
\t)
\t(symbol
\t\t(lib_id "power:GND")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{nu()}")
\t\t(property "Reference" "#PWR1"
\t\t\t(at 50 56.35 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "GND"
\t\t\t(at 50 53.81 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at 50 50 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at 50 50 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{nu()}")
\t\t)
\t\t(instances
\t\t\t(project "min"
\t\t\t\t(path "/{proj_id}"
\t\t\t\t\t(reference "#PWR1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
'''

# Verify base works
test('base', base)

# Test 1: Remove (power) from GND symbol
mod1 = base.replace('\t\t\t(power)\n', '')
test('b1_no_power', mod1)

# Test 2: Change property format (single line for simple props)
mod2 = base.replace(
    '\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
    '\t\t\t(property "Footprint" ""\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t\t)\n\t\t\t(property "Datasheet" ""\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t\t)'
)
test('b2_multiline_props', mod2)

# Test 3: Make both props multiline
mod3 = base.replace(
    '\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n\t\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
    '\t\t\t(property "Footprint" ""\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t\t)\n\t\t\t(property "Datasheet" ""\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t\t)'
)
# Also make (pin_names ...) multiline
mod3 = mod3.replace(
    '\t\t\t(pin_names (offset 0))',
    '\t\t\t(pin_names\n\t\t\t\t(offset 0)\n\t\t\t)'
)
# Also make effects multiline
mod3 = mod3.replace(
    '\t\t\t(power)',
    '\t\t\t(power)\n\t\t\t(pin_numbers hide)'
)
test('b3_multiline_full', mod3)

# Test 4: Change symbol name from "power:GND" to "GND"
mod4 = base.replace('(symbol "power:GND"', '(symbol "GND"').replace('(lib_id "power:GND")', '(lib_id "GND")')
test('b4_rename_gnd', mod4)

# Test 5: Change pin name from "GND" to "~"
mod5 = base.replace('(name "GND"', '(name "~"')
test('b5_pin_tilde', mod5)

# Test 6: Remove (pin_numbers hide) - wait, there is none. Add it.
mod6 = base.replace('\t\t\t(pin_names (offset 0))', '\t\t\t(pin_numbers hide)\n\t\t\t(pin_names (offset 0))')
test('b6_pin_num_hide', mod6)

# Test 7: Add pin_names hide
mod7 = base.replace('\t\t\t(pin_names (offset 0))', '\t\t\t(pin_names (offset 0) hide)')
test('b7_pin_name_hide', mod7)

# Test 8: Remove the newline between lib_symbols close and first instance
mod8 = base.replace(
    '\t\t)\n\t)\n\t(symbol',
    '\t\t)\n\t)\n\t(symbol'
)
test('b8_keep_same', mod8)  # should be same
