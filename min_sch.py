import uuid
nu = lambda: str(uuid.uuid4())

# Minimal KiCad 8.0 schematic: just header + lib_symbols (GND) + one GND instance + sheet_instances
sch = f'''(kicad_sch
\t(version 20231120)
\t(generator "eeschema")
\t(generator_version "8.0")
\t(uuid "{nu()}")
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
\t\t\t\t(path "/{nu()}"
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

with open('C:/Users/DELL/my-board/min.kicad_sch', 'w') as f:
    f.write(sch)
print('Minimal schematic written')
print(f'Balanced: (={sch.count("(")}, )={sch.count(")")}')
