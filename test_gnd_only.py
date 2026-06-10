import uuid, subprocess, os, re

def nu():
    return str(uuid.uuid4())

def read_lib_sym(lib, name):
    with open(f'C:/Program Files/KiCad/8.0/share/kicad/symbols/{lib}.kicad_sym', 'r', encoding='utf-8') as f:
        text = f.read()
    start = text.index(f'(symbol "{name}"')
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                sym = text[start:i+1]
                sym = sym.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"')
                sym = sym.replace(f'(symbol "{name}_', f'(symbol "{lib}:{name}_')
                return sym
        i += 1
    return text[start:]

gnd = read_lib_sym('power', 'GND')

def mk_inst(lib_id, ref, value, x, y, num_pins, fp=''):
    pins = ''
    for pn in range(1, num_pins + 1):
        pins += f'\t\t(pin "{pn}"\n\t\t\t(uuid "{nu()}")\n\t\t)\n'
    return (
        f'\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at {x} {y} 0)\n'
        f'\t\t(unit 1)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(uuid "{nu()}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f'\t\t\t(at {x} {round(y+5*1.27,2)} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "{value}"\n'
        f'\t\t\t(at {x} {round(y-5*1.27,2)} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" "{fp}"\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n'
        f'\t\t)\n'
        f'\t\t(property "Datasheet" "~"\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n'
        f'\t\t)\n'
        f'{pins}'
        f'\t\t(instances\n'
        f'\t\t\t(project "test"\n'
        f'\t\t\t\t(path "/{nu()}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f'\t\t\t\t\t(unit 1)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
    )

# Test 1: GND only with mk_inst format
sch = (
    f'(kicad_sch\n'
    f'\t(version 20231120)\n'
    f'\t(generator "eeschema")\n'
    f'\t(generator_version "8.0")\n'
    f'\t(uuid "{nu()}")\n'
    f'\t(paper "A4")\n'
    f'\t(title_block\n'
    f'\t\t(title "Test GND Only")\n'
    f'\t\t(date "2026-06-07")\n'
    f'\t\t(rev "1.0")\n'
    f'\t)\n'
    f'\t(lib_symbols\n{gnd}\n)\n'
    f'{mk_inst("power:GND", "#PWR1", "GND", 50, 50, 1)}'
    f'\t(sheet_instances\n'
    f'\t\t(path "/"\n'
    f'\t\t\t(page "1")\n'
    f'\t\t)\n'
    f'\t)\n'
    f')\n'
)

path = 'C:/Users/DELL/my-board/test_gnd_only.kicad_sch'
with open(path, 'w', encoding='utf-8') as f:
    f.write(sch)

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, text=True, timeout=30)
print(f'GND only: exit={result.returncode}')
if os.path.exists(rpt):
    print('  OK - ERC report generated')
else:
    print(f'  FAILED: {result.stderr.strip()}')
