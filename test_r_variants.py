import subprocess, re

def write_and_test(content, name, path='C:/Users/DELL/my-board'):
    fpath = f'{path}/test_r_{name}.kicad_sch'
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', fpath.replace('.kicad_sch', '.rpt'), fpath], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr

# Read the library R symbol
with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym', 'r', encoding='utf-8') as f:
    symlib = f.read()

# Find the R symbol
idx = symlib.index('(symbol "R"\n')
depth, i = 0, idx
while i < len(symlib):
    if symlib[i] == '(': depth += 1
    elif symlib[i] == ')':
        depth -= 1
        if depth == 0:
            r_sym = symlib[idx:i+1]
            break
    i += 1

# Template for minimal schematic
def make_sch(symbol_content, name_suffix):
    # Use unprefixed name (which always works)
    return f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test")
\t(paper "A4")
\t(title_block
\t\t(title "R Test {name_suffix}")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{symbol_content}
)
\t(symbol
\t\t(lib_id "R")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "220" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1"))
\t\t(pin "2" (uuid "pin2"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/"
\t\t\t\t\t(reference "R1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''

# Test variants
tests = {}

# 1. Original R symbol (with prefix Device:R to see if prefix alone is issue)
r_sym_prefix = r_sym.replace('(symbol "R"\n', '(symbol "Device:R"\n').replace('"R_', '"Device:R_')
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    r_sym_prefix = r_sym_prefix.replace(f'(property "{p}" "R"', f'(property "{p}" "Device:R"')
tests['prefix_Device_R'] = make_sch(r_sym_prefix, 'prefix_Device_R').replace('(lib_id "R")', '(lib_id "Device:R")')

# 2. Original R symbol without pin_numbers hide
r_nopin = r_sym.replace('(pin_numbers hide)\n', '')
tests['no_pin_numbers'] = make_sch(r_nopin, 'no_pin_numbers')

# 3. Without exclude_from_sim
r_nosim = r_sym.replace('(exclude_from_sim no)\n', '')
tests['no_excl_sim'] = make_sch(r_nosim, 'no_excl_sim')

# 4. Without in_bom/on_board
r_nobom = r_sym.replace('(in_bom yes)\n', '').replace('(on_board yes)\n', '')
tests['no_bom_board'] = make_sch(r_nobom, 'no_bom_board')

# 5. Remove all properties from symbol def
r_noprop = r_sym
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    r_noprop = re.sub(rf'\t+\(property "{p}" "[^"]*" \(at [^)]+\) \(effects \(font \(size [^)]+\)\)( \(hide yes\))?\)\n', '', r_noprop)
tests['no_sym_props'] = make_sch(r_noprop, 'no_sym_props')

# 6. Squash properties to single line (like the template does)
r_single = r_sym.replace('\n\t\t\t', ' ').replace('\n\t\t', ' ').replace('\n\t', ' ').replace(' \n', '\n')
# Fix the first line
r_single = r_sym  # skip, too destructive

# 7. Remove the rectangle (keep just pins) - is rectangle format issue?
r_norect = r_sym.replace('\t\t\t\t(rectangle\n\t\t\t\t\t(start -1.016 -2.54) (end 1.016 2.54)\n\t\t\t\t\t(stroke (width 0.254) (type default))\n\t\t\t\t\t(fill (type none))\n\t\t\t\t)\n', '')
tests['no_rectangle'] = make_sch(r_norect, 'no_rectangle')

# 8. Change rectangle to use inline format?
r_inlinerect = r_sym.replace('(rectangle\n\t\t\t\t\t(start -1.016 -2.54) (end 1.016 2.54)\n\t\t\t\t\t(stroke (width 0.254) (type default))\n\t\t\t\t\t(fill (type none))\n\t\t\t\t)', '(rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none)))')
tests['inline_rect'] = make_sch(r_inlinerect, 'inline_rect')

# 9. Remove (power) - wait, R doesn't have that
# 10. Strip all but the first sub-symbol
r_onepin = r_sym.replace('\t\t(symbol "R_1_1"\n\t\t\t(pin passive 0 0 0 0)\n\t\t)\n', '')
tests['one_pin_only'] = make_sch(r_onepin, 'one_pin_only')

# Run all tests
for name, content in tests.items():
    ok, err = write_and_test(content, name)
    print(f'{name}: {"OK" if ok else "FAIL"} exit={0 if ok else 3}')
