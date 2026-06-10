c = open('C:/Users/DELL/my-board/test_r_lib.kicad_sch').read()
# Check what's around position 1119
print('Context around 1119:')
print(repr(c[1100:1200]))
print()
# Check if this is actually the start of the R symbol or something else
# The search was c.find('(symbol "R"', ls) where ls=222
ls = 222
idx = c.find('(symbol "R"', ls)
print('Found at:', idx)
print('Full context:')
print(repr(c[idx-20:idx+80]))
