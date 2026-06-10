c = open('C:/Users/DELL/my-board/step2.kicad_sch').read()
# Find the R symbol in the lib_symbols section
idx = c.index('(symbol "R"')
print('R symbol at:', idx)
# Show the R symbol
end = idx
depth = 0
for i in range(idx, len(c)):
    if c[i] == '(':
        depth += 1
    elif c[i] == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
r_sym = c[idx:end]
print('R symbol length:', len(r_sym))
print('R symbol balanced:', r_sym.count('('), r_sym.count(')'))
print('Last 100 chars before R:', repr(c[idx-100:idx]))
print('First 100 chars of R:', repr(r_sym[:100]))
print('Last 100 chars of R:', repr(r_sym[-100:]))
print('After R symbol (200 chars):', repr(c[end:end+200]))
