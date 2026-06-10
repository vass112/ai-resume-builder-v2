import uuid

nu = lambda: str(uuid.uuid4())

# Create a minimal file with hand-crafted GND (known working)
hcgnd = '''\t(lib_symbols
\t(symbol "power:GND"
\t\t(pin_names hide)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(property "Reference" "#PWR"
\t\t\t(at 0 2.54 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Value" "GND"
\t\t\t(at 0 0 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at 0 0 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at 0 0 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(symbol "power:GND_0_1"
\t\t\t(pin power_in line
\t\t\t\t(at 0 0 90)
\t\t\t\t(length 0)
\t\t\t\t(hide)
\t\t\t\t(name "GND"
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
\t\t)
\t\t(symbol "power:GND_1_1"
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 1.27 -2.54)
\t\t\t\t\t(xy -1.27 -2.54) (xy 0 0)
\t\t\t\t)
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type outline))
\t\t\t)
\t\t)
\t)
)'''

# Extract library GND
with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/power.kicad_sym', 'r', encoding='utf-8') as f:
    lib_text = f.read()
start = lib_text.index('(symbol "GND"')
depth, i = 0, start
while i < len(lib_text):
    if lib_text[i] == '(': depth += 1
    elif lib_text[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
libgnd = lib_text[start:i+1]

# Print hex comparison of the two GND symbols
print("Hand-crafted GND hex dump (first 500 bytes):")
for i, c in enumerate(hcgnd[:500]):
    print(f'{i:04x}:{ord(c):04x}', end=' ' if (i+1)%10 else '\n')
print()

print("Library GND hex dump (first 500 bytes):")
for i, c in enumerate(libgnd[:500]):
    print(f'{i:04x}:{ord(c):04x}', end=' ' if (i+1)%10 else '\n')
print()

print("Hand-crafted GND repr (first 1000 chars):")
print(repr(hcgnd[:1000]))
print()

print("Library GND repr (first 1000 chars):")
print(repr(libgnd[:1000]))
print()

# Count tabs vs spaces
import re
hc_tabs = hcgnd.count('\t')
hc_spaces = len(re.findall(r' ', hcgnd))
lib_tabs = libgnd.count('\t')
lib_spaces = len(re.findall(r' ', libgnd))
print(f"Hand-crafted: {hc_tabs} tabs, {hc_spaces} spaces")
print(f"Library: {lib_tabs} tabs, {lib_spaces} spaces")
