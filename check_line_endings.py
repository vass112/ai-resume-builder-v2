import re

tpl = open('C:/Program Files/KiCad/8.0/share/kicad/template/Arduino_Nano/Arduino_Nano.kicad_sch', 'rb').read()
print(f'Template size: {len(tpl)} bytes')
print(f'CRLF count in template: {tpl.count(b"\r\n")}')
print(f'LF only count in template: {tpl.count(b"\n") - tpl.count(b"\r\n")}')

my = open('C:/Users/DELL/my-board/my-board.kicad_sch', 'rb').read()
print(f'\nMy file size: {len(my)} bytes')
print(f'CRLF count: {my.count(b"\r\n")}')
print(f'LF only count: {my.count(b"\n") - my.count(b"\r\n")}')

# Check header portion (before new lib_symbols)
ls_start = tpl.decode('utf-8').index('(lib_symbols')
header_bytes = tpl[:ls_start]
print(f'\nTemplate header bytes ending: {repr(header_bytes[-40:])}')

lib_str = '(lib_symbols'
lib_start_in_tpl = tpl.index(lib_str.encode())
header_from_tpl = tpl[:lib_start_in_tpl]
print(f'Template header CRLF: {header_from_tpl.count(b"\r\n")}')

# Now check what my generated lib_symbols and instances look like
# Search for the ESP32 instance to find generated content
my_text = my.decode('utf-8')
gen_start = my_text.find('MCU_Module:Arduino_Nano_ESP32')
# Go back to find start of the generated content (should be after lib_symbols)
gen_content = my_text[15000:18000]  # rough range
print(f'\nMy file around instances area:')
print(repr(my_text[14750:14900]))
