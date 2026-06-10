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

def extract(name):
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

template_syms = {
    'GND': extract('power:GND'),
    '+3.3V': extract('power:+3.3V'),
    '+5V': extract('power:+5V'),
    'VCC': extract('power:VCC'),
    'Conn_01x15': extract('Connector_Generic:Conn_01x15'),
}

def make_sch(sym_content, libid, val, name_suffix, pins='1'):
    pins_def = ''.join(f'\t\t(pin "{n}" (uuid "pin{n}"))\n' for n in pins.split(','))
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
{pins_def}\t\t(instances
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
    path = f'C:/Users/DELL/my-board/test_{name_suffix}.kicad_sch'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sch)
    r = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', path.replace('.kicad_sch', '.rpt'), path], capture_output=True, text=True, timeout=30)
    return r.returncode == 0

# Test: Take template Conn_01x15 body and rename to Device:R
conn_body = template_syms['Conn_01x15']

# First, what pins does Conn_01x15 use? Let's find out
import re
pin_count = len(re.findall(r'\(pin passiv "(\d+)"', conn_body))
print(f"Conn_01x15 has {pin_count} pins")

# Test original Conn_01x15
ok = make_sch(conn_body, 'Connector_Generic:Conn_01x15', 'Conn_01x15', 'conn_orig', ','.join(str(i) for i in range(1, pin_count+1)))
print(f'Conn_01x15 original: {"OK" if ok else "FAIL"}')

# Test: Rename Conn_01x15 body to Device:R
conn_as_r = conn_body.replace('(symbol "Connector_Generic:Conn_01x15"', '(symbol "Device:R"')
conn_as_r = conn_as_r.replace('"Connector_Generic:Conn_01x15_', '"Device:R_')
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    conn_as_r = conn_as_r.replace(f'(property "{p}" "Conn_01x15"', f'(property "{p}" "Device:R"')
ok = make_sch(conn_as_r, 'Device:R', 'R', 'conn_as_r', '1,2')
print(f'Conn_01x15 body as Device:R: {"OK" if ok else "FAIL"}')

# Test: Rename to power:R  
conn_as_power = conn_body.replace('(symbol "Connector_Generic:Conn_01x15"', '(symbol "power:R"')
conn_as_power = conn_as_power.replace('"Connector_Generic:Conn_01x15_', '"power:R_')
for p in ['Reference', 'Value', 'Footprint', 'Datasheet']:
    conn_as_power = conn_as_power.replace(f'(property "{p}" "Conn_01x15"', f'(property "{p}" "R"')
ok = make_sch(conn_as_power, 'power:R', 'R', 'conn_as_power', '1,2')
print(f'Conn_01x15 body as power:R: {"OK" if ok else "FAIL"}')

# Test: GND body as Device:R
gnd_body = template_syms['GND']
gnd_as_r = gnd_body.replace('(symbol "power:GND"', '(symbol "Device:R"')
ok = make_sch(gnd_as_r, 'Device:R', 'R', 'gnd_as_r', '1')
print(f'GND body as Device:R: {"OK" if ok else "FAIL"}')
