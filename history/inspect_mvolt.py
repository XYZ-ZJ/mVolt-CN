from pathlib import Path
import re
import struct
from collections import Counter, defaultdict

ROOT = Path('/mnt/c/Users/56892/Downloads/mvolt')
old = (ROOT / 'mVolt+-v0.50.2-original.exe').read_bytes()
zh = (ROOT / 'mVolt+-zh-CN-repaired.exe').read_bytes()
new = (ROOT / 'mVolt+-v0.50.4-original.exe').read_bytes()

def sections(data):
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    count = struct.unpack_from('<H', data, pe + 6)[0]
    opt = struct.unpack_from('<H', data, pe + 20)[0]
    for i in range(count):
        at = pe + 24 + opt + i * 40
        name = data[at:at + 8].rstrip(b'\0').decode('ascii')
        vsize, va, rawsize, raw = struct.unpack_from('<IIII', data, at + 8)
        yield name, va, vsize, raw, rawsize

def strings(data):
    sec = next(s for s in sections(data) if s[0] == '.rdata')
    _, va, _, raw, size = sec
    for match in re.finditer(rb'(?:[\x20-\x7e]\x00){3,}', data[raw:raw + size]):
        pos = raw + match.start()
        yield pos, 0x140000000 + va + match.start(), match.group().decode('utf-16le')

rows = []
for pos, va, english in strings(old):
    if old[pos:pos + len(english)*2] == zh[pos:pos + len(english)*2]:
        continue
    try:
        changed = zh[pos:pos + len(english)*2].decode('utf-16le').split('\0', 1)[0].rstrip()
    except UnicodeDecodeError:
        continue
    if any('\u4e00' <= c <= '\u9fff' for c in changed):
        rows.append((pos, va, english, changed))
old_by_text = defaultdict(list)
new_by_text = defaultdict(list)
for row in rows:
    old_by_text[row[2]].append(row)
for row in strings(new):
    new_by_text[row[2]].append(row)
matched = sum(min(len(value), len(new_by_text[text])) for text, value in old_by_text.items())
if __name__ == '__main__':
    print('SECTIONS OLD', list(sections(old)))
    print('SECTIONS NEW', list(sections(new)))
    print('EXTRACTED', len(rows), 'MATCHED', matched, 'OLD_ONLY', len(rows)-matched)
    print('AMBIGUOUS_TRANSLATIONS', [(text, set(row[3] for row in value)) for text, value in old_by_text.items() if len(set(row[3] for row in value)) > 1][:35])
