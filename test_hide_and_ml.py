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

# Start with new pin format AND hide keyword
r_new_hide = r_sym.replace(
    '\t\t(pin passive 0 -2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 -2.54 0)\n\t\t\t(length 0) hide\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n\t\t)'
).replace(
    '\t\t(pin passive 0 2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 2.54 0)\n\t\t\t(length 0) hide\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n\t\t)'
).replace(
    '(pin passive 0 0 0 0)',
    '(pin passive line\n\t\t\t(at 0 0 0)\n\t\t\t(length 0) hide\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n\t\t)'
)

# Also try: remove (pin_numbers hide) from the hide version
r_new_hide_nopin = r_new_hide.replace('\t(pin_numbers hide)\n', '')

# Also try: multi-line effects like the template
r_ml = r_sym.replace(
    '\t\t(pin passive 0 -2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 -2.54 0)\n\t\t\t(length 0) hide\n\t\t\t(name "~"\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(number "1"\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t)'
).replace(
    '\t\t(pin passive 0 2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 2.54 0)\n\t\t\t(length 0) hide\n\t\t\t(name "~"\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(number "2"\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t)'
).replace(
    '(pin passive 0 0 0 0)',
    '(pin passive line\n\t\t\t(at 0 0 0)\n\t\t\t(length 0) hide\n\t\t\t(name "~"\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(number "1"\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t)'
)

# Also remove pin_numbers hide from multi-line version
r_ml_nopin = r_ml.replace('\t(pin_numbers hide)\n', '')

# Also: template format but without (power) keyword
r_no_power = r_ml_nopin  # already no power

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
    return r.returncode == 0

tests = [
    ('hide_new', r_new_hide),
    ('hide_no_pinnum', r_new_hide_nopin),
    ('ml_effects', r_ml),
    ('ml_no_pinnum', r_ml_nopin),
]

for name, sym in tests:
    prefixed = sym.replace('(symbol "R"\n', '(symbol "Device:R"\n').replace('"R_', '"Device:R_')
    for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
        prefixed = prefixed.replace(f'(property "{p}" "R"', f'(property "{p}" "Device:R"')
    ok_un = make_sch(sym, 'R', 'R', f'{name}_un')
    ok_pr = make_sch(prefixed, 'Device:R', 'R', f'{name}_pr')
    print(f'{name}: un={ok_un}, pr={ok_pr}')
