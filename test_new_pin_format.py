import subprocess

with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym', 'r', encoding='utf-8') as f:
    symlib = f.read()
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

# Create a version with NEW format pins
# Old: (pin passive 0 -2.54 0 0)
# New: (pin passive line (at 0 -2.54 0) (length 0) (name "~" ...) (number "1" ...))
# We need to figure out the correct new format conversion

# In the template, the pin format is:
# (pin <type> <style>
#     (at <x> <y> <orient>)
#     (length <len>) [hide]
#     (name "<name>" (effects (font (size 1.27 1.27))))
#     (number "<num>" (effects (font (size 1.27 1.27))))
# )

# Old format: (pin <type> <style> <x> <y> <len> <orient>)
# New format (as seen in template):
# (pin <type> <style>
#     (at <x> <y> <orient>)
#     (length <len>)
#     (name "<name>" (effects ...))
#     (number "<num>" (effects ...))
# )

# For R with 2 pins:
# pin 1: passive, style=0 (line?), x=0, y=-2.54, len=0, orient=0
# pin 2: passive, style=0, x=0, y=2.54, len=0, orient=0
# sub-symbol R_1_1: pin passive 0 0 0 0

r_new_pins = r_sym.replace(
    '\t\t(pin passive 0 -2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 -2.54 0)\n\t\t\t(length 0)\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n\t\t)'
).replace(
    '\t\t(pin passive 0 2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 2.54 0)\n\t\t\t(length 0)\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n\t\t)'
).replace(
    '(pin passive 0 0 0 0)',
    '(pin passive line\n\t\t\t(at 0 0 0)\n\t\t\t(length 0)\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n\t\t)'
)

def make_sch(sym_content, libid, val, name_suffix):
    inst = f'''\t(symbol
\t\t(lib_id "{libid}")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "R1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "{val}" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
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
\t)'''
    sch = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "test-uuid")
\t(paper "A4")
\t(title_block
\t\t(title "Test {name_suffix}")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{sym_content}
)
{inst}
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''
    path = f'C:/Users/DELL/my-board/test_r_{name_suffix}.kicad_sch'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sch)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr

# Test 1: Original R (unprefixed) with new pins
print(f'R original new pins: {make_sch(r_new_pins, "R", "R", "orig_newpins")[0]}')

# Test 2: R with Device:R prefix + new pins
r_dev_new = r_new_pins.replace('(symbol "R"\n', '(symbol "Device:R"\n').replace('"R_', '"Device:R_')
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    r_dev_new = r_dev_new.replace(f'(property "{p}" "R"', f'(property "{p}" "Device:R"')
print(f'R Device:R new pins: {make_sch(r_dev_new, "Device:R", "R", "dev_newpins")[0]}')

# Also try: remove the R_1_1 sub-symbol entirely (only keep 0_1)
r_new_pins_nosub = r_new_pins.split('\n')
# Find R_1_1 and remove it
new_lines = []
skip = False
for line in r_new_pins.split('\n'):
    if '(symbol "R_1_1"' in line:
        skip = True
    if skip and line.rstrip() == '\t)':
        skip = False
        continue
    if not skip:
        new_lines.append(line)
r_no_sub = '\n'.join(new_lines)
print(f'R no R_1_1 sub: {make_sch(r_no_sub, "R", "R", "nosub")[0]}')

# Test 4: R with Device:R prefix, no R_1_1
r_dev_nosub = r_no_sub.replace('(symbol "R"\n', '(symbol "Device:R"\n').replace('"R_', '"Device:R_')
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    r_dev_nosub = r_dev_nosub.replace(f'(property "{p}" "R"', f'(property "{p}" "Device:R"')
print(f'R Device:R nosub: {make_sch(r_dev_nosub, "Device:R", "R", "dev_nosub")[0]}')
