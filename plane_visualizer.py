import json
import sys

data = json.load(sys.stdin)

print('   ABC  DEF')
for i in range(1, 26):
    print(str(i) + ' ' + (' ' if i < 10 else ''), end='')
    for j in range(6):
        print('#' if str(i) + chr(ord('A') + j) in data else '.', end='')
        if j == 2:
            print('  ', end='')
    print()
