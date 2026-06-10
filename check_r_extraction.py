dev = open('C:/Program Files/KiCad/8.0/share/kicad/symbols/Device.kicad_sym').read()

def find_matching(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    return text[start:]

# Check what text.index('(symbol "R"') finds
idx = dev.index('(symbol "R"')
print('First (symbol "R" found at', idx)
# Check context
print('Context:', dev[idx:idx+30])

# Check all symbols starting with R
import re
for m in re.finditer(r'\(symbol "R[^"]*"', dev):
    print('  Found:', m.group(), 'at', m.start())

# Now check if idx matches the correct R symbol
r_sym = find_matching(dev, idx)
print('\nExtracted R symbol length:', len(r_sym))
print('First 60 chars:', r_sym[:60])
print('Last 60 chars:', r_sym[-60:])

# Check what comes before
print('\nBefore R symbol:', repr(dev[max(0,idx-20):idx]))

# Check what comes after
aft = r_sym.find(')')
print('\nFirst close paren at offset', aft, ':', r_sym[aft:aft+10])
