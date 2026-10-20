#!/usr/bin/env python3
import hashlib
import json
import struct
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'bin_sources' / 'mVolt+-v0.50.5-original.exe'
OUTPUT = ROOT / 'mVolt+-v0.50.5-zh-CN.exe'
MANIFEST = ROOT / 'mVolt+-v0.50.5-zh-CN-manifest.json'

EXPECTED_SHA256 = '7ef2614769a6d438198bc4e6c3053469d351574515abb7a934b4dc7358047dcb'

# 1. Ensure source original binary exists (auto-download if missing)
if not SOURCE.exists():
    print("Downloading official mVolt+ v0.50.5 original from GitHub...")
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    import urllib.request
    url = "https://github.com/b00nz/mVolt/releases/download/v0.50.5/mVolt%2B.exe"
    urllib.request.urlretrieve(url, SOURCE)

# 2. Load translation dictionary (from manifest if available)
if MANIFEST.exists():
    cur_manifest = json.load(open(MANIFEST, encoding='utf-8'))
    translations = {r['english']: r['chinese'] for r in cur_manifest['translated']}
elif (ROOT / 'mVolt+-v0.50.4-zh-CN-manifest.json').exists():
    v4_manifest = json.load(open(ROOT / 'mVolt+-v0.50.4-zh-CN-manifest.json', encoding='utf-8'))
    translations = {r['english']: r['chinese'] for r in v4_manifest['translated']}
else:
    translations = {}

# 2. Add corrections and all new v0.50.5 translations
V0505_NEW_TRANSLATIONS = {
    # Fixes & disambiguations
    'Policy ': '策略 ',
    'No policies': '无可用策略',
    'Core clock': '核心频率',
    'CORE': '核心',

    # Profiles & Header
    'Apply this profile at logon': '登录时应用此方案',
    ' for editing. Not applied.': ' 供编辑。未应用。',
    'Saves the applied settings to the current profile, or as a new profile under Custom.': '保存已应用设置到当前方案，自定义下另存新方案。',
    'Applies a saved profile. A green dot means the applied settings match it; amber means they were changed since. Grey (Custom) means no saved profile is active.': '应用保存方案。绿点表示匹配，黄点表示已更改，灰点（自定义）表示未激活保存方案。',
    'Wait for the profile save to finish.': '等待方案保存完成。',
    ' with current applied settings?': '，使用当前已应用设置？',
    ', modified': '，已修改',
    'Details for ': '详情：',
    'Delete ': '删除 ',
    'Loaded ': '已载入 ',
    'Deleted ': '已删除 ',
    'Load ': '载入 ',
    'Overwrite ': '覆盖 ',

    # RTSS & PawnIO Telemetry
    'Shows the CPU temperature (Tctl on AMD, package on Intel). Needs PawnIO.': '显示 CPU 温度（AMD 为 Tctl，Intel 为封装温度）。需 PawnIO。',
    'Shows CPU package power. Needs PawnIO.': '显示 CPU 封装功率。需 PawnIO。',
    'Shows the hottest DDR5 module\'s temperature sensor. Needs PawnIO.': '显示最热 DDR5 模组温度。需 PawnIO。',
    'Opens pawnio.eu to download or reinstall PawnIO, a free signed driver. mVolt+ does not include it.': '打开 pawnio.eu 获取免费签名的 PawnIO 驱动。程序不包含该驱动。',
    'Shows used and total system memory, from Windows.': '显示已用和总系统内存（来自 Windows）。',
    'Shows the configured memory speed in MT/s, from the firmware tables.': '显示固件配置的内存速度（MT/s）。',
    'Shows how busy the CPU is across all cores, from Windows.': '显示 CPU 总体负载（来自 Windows）。',
    'Shows the average effective clock of all cores; idle cores lower it. Needs PawnIO.': '显示全核平均有效频率；空闲核会拉低。需 PawnIO。',
    'RAM used / total': '已用／总内存',
    'RAM speed': '内存速度',
    'RAM temperature': '内存温度',
    'Get PawnIO': '获取 PawnIO',
    'CPU clock': 'CPU 频率',
    'CPU load': 'CPU 负载',
    'CPU power': 'CPU 功率',
    'CPU temperature': 'CPU 温度',
    'Label color': '标签颜色',
    'Value color': '数值颜色',
    'PawnIO readings need mVolt+ to run as administrator.': 'PawnIO 读数需以管理员身份运行。',
    'CPU clock, temperature, power and RAM temperature are read through PawnIO.': 'CPU 频率、温度、功率及内存温度通过 PawnIO 读取。',
    'CPU clock, temperature, power and RAM temperature need the free PawnIO driver.': 'CPU 频率、温度、功率及内存温度需免费 PawnIO 驱动。',
    'PawnIO could not be opened, or it cannot read this CPU or memory.': '无法打开 PawnIO，或无法读取该 CPU/内存。',
    'PawnIO unavailable': 'PawnIO 不可用',
    'PawnIO not installed': 'PawnIO 未安装',
    'PawnIO ready': 'PawnIO 就绪',
    'The lines mVolt+ is sending to RTSS. Drag a line to move it; right-click it for colors. RTSS fills in the frame rate values in the game.': '发送给 RTSS 的条目。拖拽调序，右键调色。游戏内帧率数值由 RTSS 填入。',

    # V/F Flatten Above (Drop tail / Match tail)
    'Drop tail': '下压末端',
    'Match tail': '平移末端',
    'Tail dropped.': '末端已下压。',
    'Tail matched.': '末端已平移。',
    'Flatten above preview': '上方压平预览',
    'Flatten mode': '压平模式',
    'Sets the selected point to the entered frequency and flattens the points after it as the mode chooses. Hollow dots mark lowered points that the driver lifts to the plateau. Choose Apply to use it.': '将所选点设为输入频率并按模式压平后续点。空心点表示被驱动抬升至平阶的点。点应用生效。',
    'Chooses how Flatten above sets the points after the selected one.': '选择“上方压平”如何设置所选点之后的各点。',
    'Shows both modes on this curve as the GPU warms. Drop tail lowers the later points by one large offset, so they stay flat; this is the generally recommended way to undervolt, also in Afterburner. Match tail gives each point its own offset: exact now, but warming can lift some above the selected point. The slider shows how heat from real workloads could shift each tail; the thin line is without warming.': '展示升温时两种压平表现。下压末端统一加大负偏移以保持水平（常规推荐降压法）；平移末端为各点单独设偏移，升温可能抬升部分点。滑块展示发热影响；细线为未升温状态。',
    'Drop tail would move a later point outside the supported frequency range. Select a higher point or use Match tail.': '下压末端会导致后续点超出频率范围。请选更高的点或用平移末端。',
    'Pending curve restored.': '已恢复待应用曲线。',
    'Offset staged for the selected region.': '所选区域偏移已暂存。',
    'Point staged by dragging.': '拖动设置的点已暂存。',
    'Point staged.': '点已暂存。',
    'Points': '各点',
    'Point': '点',
    'Global': '全局',

    # BIOS Override & Recovery
    'Removing BIOS override': '正在移除 BIOS 覆盖',
    'The GPU could not be restarted. Restart Windows.': '无法重启 GPU。请重启 Windows。',
    'The stored BIOS override changed.': '已保存的 BIOS 覆盖已改变。',
    'The GPU did not recover. Restart Windows to complete recovery.': 'GPU 未恢复。请重启 Windows 完成恢复。',
    'The BIOS override could not be removed. Try again.': '无法移除 BIOS 覆盖。请重试。',
    'Repair permissions': '修复权限',
    'Repairing permissions': '正在修复权限',
    'Repair unused recovery storage permissions and retry. GPU settings and recovery files are preserved.': '修复恢复存储权限并重试。GPU 设置及恢复文件保留。',
    'Load BIOS file only previews the copy. Nothing changes until you save and restart.': '载入 BIOS 仅预览副本。保存并重启前不作更改。',
    'In both modes:': '两种模式下：',
    ' Saved limits stay active after restarting Windows, until you choose Use original limits.': ' 保存的限制在重启 Windows 后依然有效，直到选“使用原始限制”。',
    ' Your graphics card\'s BIOS is NOT flashed or overwritten.': ' 显卡 BIOS 不会被刷写或覆盖。',
    'Needs driver 616 or newer.': '需 616 或更新版驱动。',
    'Save this BIOS, restart, then edit its limits.': '保存此 BIOS，重启后编辑限制。',
    'Restart first': '先重启系统',
    ' Direct (default): stores only the changed limits. No BIOS file is needed.': ' Direct（默认）：仅保存修改后的限制。无需 BIOS 文件。',
    'For BIOS file, use a copy (.rom) of your own graphics card\'s BIOS:': 'BIOS 文件模式请使用显卡自身的 BIOS 副本 (.rom)：',
    'Fan layout': '风扇布局',
    'Active value': '当前生效值',
    'New value': '设定新值',
    'New minimum': '新最小值',
    'Board input current': '整卡输入电流',
    'Curve running ': '曲线运行中 ',

    # About Window & Context Menus
    'Shows the version, the project page and third-party notices.': '显示版本、项目主页及第三方声明。',
    'Project page': '项目主页',
    'Source': '源码',
    'Third-party components': '第三方组件',
    'PawnIO modules 0.2.11': 'PawnIO 模块 0.2.11',
    'PawnIO\'s signed read modules, used for the overlay\'s CPU and RAM readings. The PawnIO driver is not included.': 'PawnIO 签名读取模块，用于 CPU/内存读数。不含驱动。',
    '&Copy': '复制&C',
    '&Paste': '粘贴(&P)',
    '&Delete': '删除(&D)',
    '&Undo': '撤销&U',
    'Cu&t': '剪切&T',
    'Select &All': '全选(&A)',
    'Accent color': '强调色',
    'Primary text': '主要文本',
    'Debug report': '调试报告',
}

translations.update(V0505_NEW_TRANSLATIONS)

source = SOURCE.read_bytes()
digest = hashlib.sha256(source).hexdigest()
if digest != EXPECTED_SHA256:
    raise SystemExit(f"Unexpected source SHA-256: {digest}")

def seal_positions(data):
    at = data.find(b'mVolt+ seal v1')
    if at < 0 or data.find(b'mVolt+ seal v1', at + 1) >= 0:
        raise ValueError('seal not unique')
    size, checksum, _, digest = struct.unpack_from('<IIII', data, at + 16)
    if size != len(data) or digest != at + 32:
        raise ValueError('unexpected seal layout')
    return checksum, digest

def sealed_digest(data):
    checksum, digest = seal_positions(data)
    masked = bytearray(data)
    masked[checksum:checksum + 4] = bytes(4)
    masked[digest:digest + 32] = bytes(32)
    return hashlib.sha256(masked).digest()

def pe_checksum(data, offset):
    total = 0
    for i in range(0, len(data), 4):
        if i == offset: continue
        word = int.from_bytes(data[i:i + 4], 'little')
        total = (total & 0xffffffff) + word + (total >> 32)
        total = (total & 0xffffffff) + (total >> 32)
    total = (total & 0xffff) + (total >> 16)
    total = total + (total >> 16)
    return (total & 0xffff) + len(data)

orig_checksum, orig_digest = seal_positions(source)
if sealed_digest(source) != source[orig_digest:orig_digest + 32]:
    raise SystemExit("Original integrity seal does not match")

output = bytearray(source)

# Restrict replacement to .rdata
# In v0.50.5: raw_start = 0x2b0800, raw_end = 0x34a200
raw_start = 0x2b0800
raw_end = 0x34a200
base_va = 0x140000000 + 0x2b2000 - raw_start

translated = []
skipped = []

for match in re.finditer(rb'(?:[\x20-\x7e]\x00){3,}', source[raw_start:raw_end]):
    offset = raw_start + match.start()
    va = base_va + offset
    english = match.group().decode('utf-16le')
    chinese = translations.get(english)
    if not chinese or chinese == english:
        continue

    # Guard against crossing ASCII/UTF-16 boundaries
    if offset >= 2 and 0x20 <= source[offset - 1] <= 0x7e and 0x20 <= source[offset - 2] <= 0x7e:
        skipped.append({'offset': hex(offset), 'va': hex(va), 'english': english, 'reason': 'ascii_boundary'})
        continue

    before_bytes = english.encode('utf-16le')
    after_bytes = chinese.encode('utf-16le')
    if len(after_bytes) > len(before_bytes):
        skipped.append({'offset': hex(offset), 'va': hex(va), 'english': english, 'chinese': chinese, 'reason': 'too_long'})
        continue

    terminated = source[offset + len(before_bytes):offset + len(before_bytes) + 2] == b'\0\0'
    pad = bytes(len(before_bytes) - len(after_bytes)) if terminated else ' '.encode('utf-16le') * ((len(before_bytes) - len(after_bytes)) // 2)
    output[offset:offset + len(before_bytes)] = after_bytes + pad

    source_tag = 'v0.50.5_new' if english in V0505_NEW_TRANSLATIONS else 'v0.50.4_reused'
    translated.append({
        'offset': hex(offset),
        'va': hex(va),
        'english': english,
        'chinese': chinese,
        'source': source_tag,
        'embedded_prefix': not terminated
    })

# Verify internal configuration keys are intact
for key in (b"gpu_clock_range\0", b"core_clock_offset\0", b"profile_save_mode_chosen\0", b"power_policy_layout\0", b"active_profile\0"):
    if source.count(key) != output.count(key):
        raise SystemExit(f"An internal key changed: {key!r}")

# Recompute seal and PE checksum
checksum_offset, digest_offset = seal_positions(output)
output[digest_offset:digest_offset + 32] = sealed_digest(output)
struct.pack_into('<I', output, checksum_offset, pe_checksum(output, checksum_offset))

if sealed_digest(output) != output[digest_offset:digest_offset + 32]:
    raise SystemExit("Translated integrity seal does not match")
if struct.unpack_from('<I', output, checksum_offset)[0] != pe_checksum(output, checksum_offset):
    raise SystemExit("PE checksum mismatch")
if len(output) != len(source):
    raise SystemExit("Output file size changed")

# Verify that changed bytes are only within allowed boundaries
allowed = bytearray(len(source))
for row in translated:
    pos = int(row['offset'], 16)
    eng_len = len(row['english'].encode('utf-16le'))
    allowed[pos:pos + eng_len] = bytes([1]) * eng_len

allowed[digest_offset:digest_offset + 32] = bytes([1]) * 32
allowed[checksum_offset:checksum_offset + 4] = bytes([1]) * 4

changed_bytes = 0
for offset, (before, after) in enumerate(zip(source, output)):
    if before != after:
        changed_bytes += 1
        if not allowed[offset]:
            raise SystemExit(f"Unexpected changed byte at {hex(offset)}")

out_sha256 = hashlib.sha256(output).hexdigest()
OUTPUT.write_bytes(output)

manifest = {
    'source_sha256': digest,
    'output_sha256': out_sha256,
    'translation_count': len(translated),
    'skipped_count': len(skipped),
    'changed_bytes': changed_bytes,
    'file_size': len(output),
    'translated': translated,
    'skipped': skipped
}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

print(f"Successfully generated {OUTPUT.name}!")
print(f"  Translations: {len(translated)}")
print(f"  Skipped (safety guards): {len(skipped)}")
print(f"  Changed bytes: {changed_bytes}")
print(f"  Output SHA-256: {out_sha256}")
print(f"  Output file size: {len(output)}")