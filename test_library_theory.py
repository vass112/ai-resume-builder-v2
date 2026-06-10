import subprocess

with open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch', 'r', encoding='utf-8') as f:
    tpl = f.read()

ls_start = tpl.index('(lib_symbols')
depth, i = 0, ls_start
while i < len(tpl):
    if tpl[i] == '(': depth += 1
    elif tpl[i] == ')':
        depth -= 1
        if depth == 0:
            ls_section = tpl[ls_start:i+1]
            break
    i += 1

# Extract multiple symbols from template
def extract_symbol(name):
    idx = ls_section.index(f'(symbol "{name}"')
    depth, i = 0, idx
    while i < len(ls_section):
        if ls_section[i] == '(': depth += 1
        elif ls_section[i] == ')':
            depth -= 1
            if depth == 0:
                return ls_section[idx:i+1]
        i += 1
    return None

template_symbols = {
    'power:GND': extract_symbol('power:GND'),
    'power:+3.3V': extract_symbol('power:+3.3V'),
    'power:+5V': extract_symbol('power:+5V'),
    'power:VCC': extract_symbol('power:VCC'),
    'Connector_Generic:Conn_01x15': extract_symbol('Connector_Generic:Conn_01x15'),
}

# Also extract Device:R from library  
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

# Make the R symbol with Device:R prefix
r_dev = r_sym.replace('(symbol "R"\n', '(symbol "Device:R"\n').replace('"R_', '"Device:R_')
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    r_dev = r_dev.replace(f'(property "{p}" "R"', f'(property "{p}" "Device:R"')

def make_sch(symbol_content, libid, val, extra=''):
    inst = f'''\t(symbol
\t\t(lib_id "{libid}")
\t\t(at 50 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "inst-uuid")
\t\t(property "Reference" "X1" (at 50 56.35 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "{val}" (at 50 43.65 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Datasheet" "~" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "pin1"))
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/"
\t\t\t\t\t(reference "X1")
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
\t\t(title "Test {libid.replace(':', '_')}")
\t\t(date "2026-06-07")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{symbol_content}
)
{inst}
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)'''
    path = f'C:/Users/DELL/my-board/test_v_{libid.replace(":", "_")}.kicad_sch'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sch)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr

# Test each template symbol standalone
for name, sym in template_symbols.items():
    lib = name.split(':')[0]
    symname = name.split(':')[1]
    ok, err = make_sch(sym, name, symname)
    print(f'{name}: {"OK" if ok else "FAIL"}')

# Test Device:R from library
print(f'Device:R (lib extract): {"OK" if make_sch(r_dev, "Device:R", "R")[0] else "FAIL"}')
