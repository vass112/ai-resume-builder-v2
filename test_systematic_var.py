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

# Convert to new pin format
r_new = r_sym.replace(
    '\t\t(pin passive 0 -2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 -2.54 0)\n\t\t\t(length 0)\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n\t\t)'
).replace(
    '\t\t(pin passive 0 2.54 0 0)',
    '\t\t(pin passive line\n\t\t\t(at 0 2.54 0)\n\t\t\t(length 0)\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n\t\t)'
).replace(
    '(pin passive 0 0 0 0)',
    '(pin passive line\n\t\t\t(at 0 0 0)\n\t\t\t(length 0)\n\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n\t\t)'
)

# Create variants
variants = {}

# A: Remove pin_numbers hide
variants['no_pinnums'] = r_new.replace('\t(pin_numbers hide)\n', '')

# B: Remove (exclude_from_sim no)
variants['no_excl_sim'] = r_new.replace('\t(exclude_from_sim no)\n', '')

# C: Remove both
variants['no_both'] = r_new.replace('\t(pin_numbers hide)\n', '').replace('\t(exclude_from_sim no)\n', '')

# D: Remove (in_bom yes) and (on_board yes)  
variants['no_bom'] = r_new.replace('\t(in_bom yes)\n', '').replace('\t(on_board yes)\n', '')

# E: Make pin_names single-line with hide (like library format)
r_pinhide = r_new.replace(
    '\t(pin_names\n\t\t(offset 0)\n\t)',
    '\t(pin_names (offset 0) hide)'
)
variants['pin_names_hide'] = r_pinhide

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

# Test each variant with both unprefixed and prefixed
for name, sym in variants.items():
    ok_un, _ = make_sch(sym, 'R', 'R', f'{name}_un')
    prefixed_sym = sym.replace('(symbol "R"\n', '(symbol "Device:R"\n').replace('"R_', '"Device:R_')
    for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
        prefixed_sym = prefixed_sym.replace(f'(property "{p}" "R"', f'(property "{p}" "Device:R"')
    ok_pr, _ = make_sch(prefixed_sym, 'Device:R', 'R', f'{name}_pr')
    print(f'{name}: unprefixed={"OK" if ok_un else "FAIL"}, prefixed={"OK" if ok_pr else "FAIL"}')
