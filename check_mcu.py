c = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/MCU_Module.kicad_sym').read()
idx = c.find('(symbol "Arduino_Nano_ESP32"')
print(f'Found at {idx}')
if idx >= 0:
    print(c[idx:idx+300])
else:
    for pat in ['Arduino_Nano_ESP32', 'ESP32']:
        i = c.find(pat)
        if i >= 0:
            print(f'Found "{pat}" at {i}')
            print(c[max(0,i-50):i+150])
