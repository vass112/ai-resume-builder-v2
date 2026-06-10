text = open('C:/Users/DELL/my-board/my-board.kicad_sch', 'r', encoding='utf-8').read()

# Find all top-level balanced structures
def find_block(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1], i+1
        i += 1
    return text[start:], len(text)

# Find overall structure
pos = 0
level = 0
blocks = []
while pos < len(text):
    if text[pos] == '(':
        block, end = find_block(text, pos)
        # Only capture top-level blocks
        if level == 0:
            blocks.append(block[:80])  # first 80 chars
            blocks.append('...' + block[-80:])  # last 80 chars
        pos = end
    else:
        pos += 1

print("Top-level blocks:")
for i, b in enumerate(blocks):
    print(f'Block {i//2+1} {"start" if i%2==0 else "end"}: {repr(b)}')
    if i > 20:
        break
