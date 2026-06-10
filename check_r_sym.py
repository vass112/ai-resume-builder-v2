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

r_sym = find_matching(dev, dev.index('(symbol "R"'))
print('R symbol from Device.kicad_sym:')
print(r_sym[:400])
print('...')
print('Last 200:', r_sym[-200:])
print('\nSymbol length:', len(r_sym))
print('Balanced: (=%d, )=%d' % (r_sym.count('('), r_sym.count(')')))
