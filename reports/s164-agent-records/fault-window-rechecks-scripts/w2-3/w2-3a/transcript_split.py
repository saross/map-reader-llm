"""W2-3a: split the grep_cmds.py dump of a session archive into blocks.

Filters the blocks by agent and regular expression; used to find the original commands.
"""
import re
import sys

path, agent, rx = sys.argv[1], sys.argv[2], sys.argv[3]
maxlen = int(sys.argv[4]) if len(sys.argv) > 4 else 600
text = open(path).read()
blocks = re.split(r"(?m)^(?=## )", text)
for b in blocks:
    head = b.split("\n", 1)[0]
    if agent not in head:
        continue
    if not re.search(rx, b):
        continue
    print(b[:maxlen].rstrip())
    print()
