c = open('C:/Users/DELL/my-board/min.kicad_sch').read()
print('min file has (symbol "R":', '(symbol "R"' in c)
# Search for any R-related symbol names in the min file
import re
for m in re.finditer(r'\(symbol "([^"]*R[^"]*)"', c):
    print('Found symbol with R:', m.group(1), 'at', m.start())
# Check if there's any stray "R" inside the content
for m in re.finditer(r'\(symbol "R"', c):
    print('Found (symbol "R" at', m.start(), 'context:', c[m.start():m.start()+50])
# Now check the test_r_lib file for the SAME thing
c2 = open('C:/Users/DELL/my-board/test_r_lib.kicad_sch').read()
for m in re.finditer(r'\(symbol "R"', c2):
    print('R found at', m.start(), 'context:', c2[m.start():m.start()+80])
