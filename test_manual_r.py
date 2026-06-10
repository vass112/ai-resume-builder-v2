import uuid, subprocess, os

nu = lambda: str(uuid.uuid4())

# Exact working minimal content
min_content = open('C:/Users/DELL/my-board/min.kicad_sch', 'r').read()

# Manually define R symbol (copied from Device.kicad_sym, converted to \n)
# This is the EXACT content from Device.kicad_sym, but with \n only
r_manual = '''(symbol "R"
\t\t(pin_numbers hide)
\t\t(pin_names
\t\t\t(offset 0)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(property "Reference" "R"
\t\t\t(at 2.032 0 90)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "R"
\t\t\t(at 0 0 90)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at -1.778 0 90)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at 0 0 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Description" "Resistor"
\t\t\t(at 0 0 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "ki_keywords" "R res resistor"
\t\t\t(at 0 0 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "ki_fp_filters" "R_*"
\t\t\t(at 0 0 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(symbol "R_0_1"
\t\t\t(rectangle
\t\t\t\t(start -1.016 -2.54) (end 1.016 2.54)
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type none))
\t\t\t)
\t\t)
\t\t(symbol "R_1_1"
\t\t\t(pin passive line
\t\t\t\t(at 0 3.81 270)
\t\t\t\t(length 1.27)
\t\t\t\t(name "~"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "1"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 0 -3.81 90)
\t\t\t\t(length 1.27)
\t\t\t\t(name "~"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "2"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''

# Add R symbol at the end of lib_symbols (before the closing paren)
# Find the first instance start
inst_start = min_content.find('\t(symbol\n\t\t(lib_id "power:GND")')
# Everything before instances is header + lib_symbols
before = min_content[:inst_start]
# The last character of before should be ) closing lib_symbols
# We need to insert R before it
# Actually find the exact position
ls_content_end = before.rfind(')')
header_part = min_content[:ls_content_end]
closing_paren = min_content[ls_content_end:inst_start]

content = header_part + '\n' + r_manual + '\n' + closing_paren + min_content[inst_start:]
# Actually, let me just find the lib_symbols closing
ls = content.find('(lib_symbols')
depth = 0
ls_end = ls
for i in range(ls, len(content)):
    if content[i] == '(': depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break

# Insert R before lib_symbols close
new_content = content[:ls_end-1] + '\n' + r_manual + '\n' + content[ls_end-1:]

# Also add R1 instance (just after GND instance)
gnd_inst_end = new_content.find('(sheet_instances')
r1_inst = '''\t(symbol
\t\t(lib_id "Device:R")
\t\t(at 80 50 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "''' + nu() + '''")
\t\t(property "Reference" "R1"
\t\t\t(at 80 56.35 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "220"
\t\t\t(at 80 53.81 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
\t\t\t(at 80 50 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at 80 50 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(pin "1"
\t\t\t(uuid "''' + nu() + '''")
\t\t)
\t\t(pin "2"
\t\t\t(uuid "''' + nu() + '''")
\t\t)
\t\t(instances
\t\t\t(project "test"
\t\t\t\t(path "/''' + nu() + '''"
\t\t\t\t\t(reference "R1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
'''

new_content = new_content[:gnd_inst_end] + r1_inst + '\n' + new_content[gnd_inst_end:]

o = new_content.count('(')
c = new_content.count(')')
print('Balanced:', o, c, 'OK' if o==c else 'UNBALANCED!')

path = 'C:/Users/DELL/my-board/test_manual_r.kicad_sch'
with open(path, 'w') as f:
    f.write(new_content)

rpt = path.replace('.kicad_sch', '.rpt')
try: os.remove(rpt)
except: pass
result = subprocess.run(['C:/Program Files/KiCad/8.0/bin/kicad-cli.exe', 'sch', 'erc', '-o', rpt, path], capture_output=True, timeout=30)
if os.path.exists(rpt):
    with open(rpt) as f:
        report = f.read()
    errors = len([l for l in report.split('\n') if 'error' in l.lower()])
    warnings = len([l for l in report.split('\n') if 'warning' in l.lower()])
    print(f'Test: OK ({errors} err, {warnings} warn)')
else:
    print(f'Test: FAIL (exit={result.returncode})')
