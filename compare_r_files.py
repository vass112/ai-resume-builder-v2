import re

with open('C:/Users/DELL/my-board/test_hand_r.kicad_sch', 'r', encoding='utf-8') as f:
    hand = f.read()

with open('C:/Users/DELL/my-board/test_literal_r.kicad_sch', 'r', encoding='utf-8') as f:
    prog = f.read()

# Normalize both
def norm(s):
    s = re.sub(r'uuid "[^"]*"', 'uuid U', s)
    s = re.sub(r'"[0-9a-f-]{36}"', '"U"', s)
    return s

hand_n = norm(hand)
prog_n = norm(prog)

print(f'Hand size: {len(hand)}, Prog size: {len(prog)}')
print(f'Hand balanced: {hand.count("(")}/{hand.count(")")}')
print(f'Prog balanced: {prog.count("(")}/{prog.count(")")}')

# Compare line by line
h_lines = hand_n.split('\n')
p_lines = prog_n.split('\n')
print(f'Hand has {len(h_lines)} lines, Prog has {len(p_lines)} lines')

# Find all differences
diffs = 0
for i in range(max(len(h_lines), len(p_lines))):
    h = h_lines[i] if i < len(h_lines) else '<EOF>'
    p = p_lines[i] if i < len(p_lines) else '<EOF>'
    if h != p:
        diffs += 1
        if diffs <= 15:
            print(f'Diff line {i+1}:')
            print(f'  hand: {repr(h[:120])}')
            print(f'  prog: {repr(p[:120])}')
print(f'Total diffs: {diffs}')

# Check if hand file tabs were preserved
with open('C:/Users/DELL/my-board/test_hand_r.kicad_sch', 'rb') as f:
    raw_hand = f.read()
tab_count = raw_hand.count(0x09)
spaces = raw_hand.count(0x20)
lines = raw_hand.count(0x0a)
print(f'\nHand file: {tab_count} tabs, {spaces} spaces, {lines} lines')
