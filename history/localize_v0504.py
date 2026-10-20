#!/usr/bin/env python3
"""Rebuild the v0.50.4 Chinese candidate from verified original executables."""
from pathlib import Path
import hashlib
import json
import struct

from inspect_mvolt import ROOT, old, zh, new, old_by_text, sections, strings

SOURCE_SHA256 = '704662c128e5a3f453d67f271878ff9a794147d2f326b351031aa2944a2832df'
OLD_SHA256 = 'd54c92501606ada232caaa74e1ca0c622776fe26ecdf15be94f745cceec08ec1'
OLD_ZH_SHA256 = 'f1fce3e54a9872993ee1788d5a60d5be60170315ff5c6a93bf16381f0be67eb1'
OUTPUT = Path(__file__).resolve().parent / 'mVolt+-v0.50.4-zh-CN.exe'
MANIFEST = Path(__file__).resolve().parent / 'mVolt+-v0.50.4-zh-CN-manifest.json'

CORRECTIONS = {
    'Policy ': '策略 ',
    'No policies': '无可用策略',
    'Core clock': '核心频率',
    'CORE': '核心',
}

NEW_TRANSLATIONS = {
    'BIOS override': 'BIOS 覆盖',
    'Theoretical max.': '理论最大值',
    'BIOS default': 'BIOS 默认值',
    'Profile details ': '配置详情 ',
    'Profile details for ': '配置详情：',
    'Profile parameters': '配置参数',
    'Parameters': '参数',
    'Save applied settings': '保存已应用设置',
    'Apply shortcut': '应用快捷键',
    'Saving shortcut': '保存快捷键',
    'Shortcut saved.': '快捷键已保存。',
    'Shortcut cleared.': '快捷键已清除。',
    'Shortcut save failed: ': '快捷键保存失败：',
    'Shortcut saved for ': '已保存快捷键：',
    'Saving profile name': '保存方案名称',
    'Profile renamed.': '方案已重命名。',
    'Profile renamed to ': '方案重命名为 ',
    'Profile rename failed: ': '方案重命名失败：',
    'Save current as': '当前设置另存为',
    'No enabled settings': '无已启用设置',
    'Clock offsets': '频率偏移',
    'Power & voltage': '功率与电压',
    'Active ranges': '生效范围',
    'PWM frequency': 'PWM 频率',
    'Speedo': 'Speedo',
    'Speedo is unavailable.': 'Speedo 不可用。',
    'Original Speedo: ': '原始 Speedo：',
    'Load a BIOS copy to edit BIOS limits.': '载入 BIOS 副本以编辑 BIOS 限制。',
    'BIOS override is not available on this system': '此系统不支持 BIOS 覆盖',
    'Change firmware clock ranges, power and voltage limits.': '修改固件频率范围、功率及电压限制。',
    'Not available for this BIOS.': '此 BIOS 不支持。',
    'PWM frequency is unavailable.': 'PWM 频率不可用。',
    'Choose a supported fan layout.': '选择受支持的风扇布局。',
    'Apply GPU curve': '应用 GPU 曲线',
    'Invalid curve points.': '曲线点无效。',
    'No active fan channels are selected.': '未选中活动风扇通道。',
    'No supported fan frequency table is available.': '没有受支持的风扇频率表。',
    'Toggle RTSS overlay': '切换 RTSS 叠加层',
    'Core clock offset': '核心频率偏移',
    'NVVDD OCP maximum': 'NVVDD OCP 上限',
    'MSVDD OCP maximum': 'MSVDD OCP 上限',
    'Minimum value: ': '最小值：',
    'The profile list is full.': '配置方案列表已满。',
    'That profile is no longer available.': '该配置方案已不可用。',
    'Wait for the current operation to finish.': '请等待当前操作完成。',
    'Could not start deleting the profile.': '无法开始删除配置方案。',
    'Could not start renaming the profile.': '无法开始重命名配置方案。',
    'The RTSS visibility setting is invalid.': 'RTSS 可见性设置无效。',
    'Could not load RTSS visibility: ': '无法读取 RTSS 可见性：',
    'Could not save RTSS visibility: ': '无法保存 RTSS 可见性：',
    'Could not save RTSS visibility. ': '无法保存 RTSS 可见性。',
    'Could not start saving RTSS visibility.': '无法开始保存 RTSS 可见性。',
    'Could not start saving the shortcut.': '无法开始保存快捷键。',
    'That shortcut is already assigned to the RTSS overlay.': '该快捷键已分配给 RTSS 叠加层。',
    'Enter a profile name of at most 128 UTF-8 bytes.': '配置方案名称最多 128 个 UTF-8 字节。',
    'That profile name already exists.': '该配置方案名称已存在。',
    'Profiles cannot be deleted in this mode.': '此模式下不能删除配置方案。',
    'Profiles cannot be renamed in this mode.': '此模式下不能重命名配置方案。',
    'Could not start saving the shortcut.': '无法开始保存快捷键。',
    'No active fan channels are selected.': '未选中活动风扇通道。',
    'The modern fan topology interface is unavailable.': '新式风扇拓扑接口不可用。',
    'The legacy fan interface is unavailable.': '旧式风扇接口不可用。',
    'The driver returned invalid legacy fan settings.': '驱动返回的旧式风扇设置无效。',
    'The native fan layout could not be verified.': '无法验证原生风扇布局。',
    'The legacy fan channel or its policy is no longer available.': '旧式风扇通道或其策略已不可用。',
    'The legacy fan request did not retain the requested policy and duty.': '旧式风扇请求未保留指定策略和占空比。',
    'The fan request no longer matches its policy or fresh duty range.': '风扇请求与策略或当前占空比范围不匹配。',
    'GPU fan policies need unique identities, increasing temperatures and nondecreasing valid speeds.': 'GPU 风扇策略须有唯一标识，温度递增且转速不得下降。',
    'GPU fan points need increasing temperatures and nondecreasing speeds within the numeric range.': 'GPU 风扇点温度须递增，转速须在范围内且不得下降。',
    'GPU fan speed coordinates require the v14 document schema.': 'GPU 风扇转速坐标需要 v14 文档结构。',
    'GPU fan speed is outside the supported numeric range.': 'GPU 风扇转速超出支持的数值范围。',
    'PWM frequency is outside its BIOS field.': 'PWM 频率超出 BIOS 字段范围。',
    'Choose 25 or 27 kHz.': '请选择 25 或 27 kHz。',
    'Saving prepares the selected layout for restart.': '保存后，所选布局将在重启后生效。',
    'Saving prepares the range for restart; your tuning offset stays unchanged.': '保存后频率范围将在重启后生效；调校偏移不变。',
    'The original BIOS configuration retained before these overrides.': '覆盖前保存的原始 BIOS 配置。',
    'The original driver-reported Speedo retained before mVolt+ overrides.': 'mVolt+ 覆盖前保存的驱动原始 Speedo。',
    'Effective Speedo reported by the driver, using the same reading as Telemetry.': '驱动报告的生效 Speedo，与监控数据读数相同。',
    'Default operating limit reported for the active BIOS.': '当前 BIOS 报告的默认运行上限。',
    'A separate fixed default operating voltage is not reported for this ceiling.': '该上限未报告单独的固定默认运行电压。',
    'Frequency declared by the confirmed active BIOS input, not a measured waveform. Mixed means the active rows differ.': '已确认的当前 BIOS 输入所声明的频率，并非实测波形。“混合”表示活动行不同。',
    'Allowed clock offset range declared by this BIOS before mVolt+ overrides, in MHz.': 'mVolt+ 覆盖前，此 BIOS 声明的允许频率偏移范围，单位 MHz。',
    'Allowed offsets from the BIOS clock, in MHz. Zero applies no offset.': '相对 BIOS 频率的允许偏移，单位 MHz；零表示不偏移。',
    'Zero offset from the active BIOS\'s memory clock.': '相对当前 BIOS 显存频率的零偏移。',
    'The native clock range does not match a supported BIOS declaration.': '原生频率范围与受支持的 BIOS 声明不匹配。',
    'Limits are not verified. Open Settings > Advanced tuning > BIOS override.': '限制尚未验证。请打开“设置 > 高级调校 > BIOS 覆盖”。',
    'Step 2 of 2: load a BIOS copy to edit BIOS limits.': '第 2 步，共 2 步：载入 BIOS 副本以编辑限制。',
    'This board has no auxiliary current request.': '此显卡没有辅助电流请求。',
    'The selected OCP control identity changed.': '所选 OCP 控件标识已变化。',
    'Enter a whole MHz value within the offset range.': '请输入偏移范围内的整数 MHz 值。',
    'Enter a whole value from 0 to 4294967295.': '请输入 0 至 4294967295 的整数。',
    'The Core V/F layout changed; reload the curve before editing.': '核心 V/F 布局已变化；请重新载入曲线。',
    'The V/F mode and point mask do not match a supported layout.': 'V/F 模式与点掩码不匹配受支持的布局。',
    'The V/F frequency baseline or stored offset is invalid.': 'V/F 频率基线或保存的偏移无效。',
    'The legacy V/F records do not match their advertised topology.': '旧式 V/F 记录与声明的拓扑不匹配。',
    'The profile V/F point count does not match this GPU.': '配置方案 V/F 点数与此 GPU 不匹配。',
    'Restoring the original V/F offsets failed: the original layout could not be revalidated.': '恢复原始 V/F 偏移失败：无法重新验证原始布局。',
    'GPU fan policy readback is unavailable. The profile was not saved.': 'GPU 风扇策略回读不可用，配置方案未保存。',
    'This profile file was created by a newer mVolt+ version. It has been left untouched.': '此配置方案由新版 mVolt+ 创建，文件未被修改。',
    'Profile delete failed: ': '删除方案失败：',
    'Profile load failed: ': '载入方案失败：',
    'Profile save failed: ': '保存方案失败：',
    'Delete profile ': '删除配置方案 ',
    'Overwrite profile ': '覆盖配置方案 ',
    'Saved current settings to ': '当前设置已保存至 ',
    ' with current applied settings': '，使用当前已应用设置',
    ' Retrying automatically.': ' 正在自动重试。',
    'Memory clock in the driver\'s frequency convention; command-clock conversion is unavailable.': '驱动频率口径下的显存频率；无法换算命令频率。',
    'Memory command clock. Driver-reported frequency: ': '显存命令频率。驱动报告频率：',
    'The frequency for the selected point. Press Enter to set and apply it, or choose Set point to stage it.': '所选点的频率。按 Enter 设置并应用，或选择“设置点”暂存。',
    'A frequency offset for the selected points. Press Enter to set and apply it, or choose Set offset to stage it.': '所选点的频率偏移。按 Enter 设置并应用，或选择“设置偏移”暂存。',
    'Shows the curve without your clock and point offsets, for comparison. Older Core and domain references are estimates.': '显示未加入频率及点偏移的曲线供比较。旧版核心和频域参考曲线是估算值。',
    'Twice the original PLL maximum minus the stock P0 memory clock. Guidance only; higher values can be entered.': '原始 PLL 上限的两倍减去原厂 P0 显存频率。仅供参考，可输入更高值。',
    'PWM carrier frequency. This does not switch between RPM and PWM control modes or set fan speed.': 'PWM 载波频率。不会切换 RPM/PWM 模式或设置风扇转速。',
    'Logical fan control channels. Several physical fans can share a channel. Zero means no active logical channels, not zero fan speed.': '逻辑风扇控制通道。多个实体风扇可共用通道；零表示没有活动通道，而非转速为零。',
    'Upper bound of the driver\'s Speedo model range, as shown in Telemetry. Guidance only; higher values can be entered.': '驱动 Speedo 模型范围上限，与监控数据一致。仅供参考，可输入更高值。',
    'Sets the carrier frequency on the selected layout\'s active rows. Saving prepares the change for restart.': '设置所选布局活动行的载波频率。保存后将在重启后生效。',
    'Requested PWM duty, from 0 to 100%, increasing or staying level down the column. A zero request may not stop the fan.': '请求的 PWM 占空比为 0 至 100%，沿列递增或持平。请求零不一定会停转。',
    'Requested whole-number RPM, increasing or staying level down the column. The 0': '请求的整数 RPM，沿列递增或持平。0',
    '32767 entry range is an encoding limit, not the fan\'s measured range.': '32767 的输入范围是编码限制，并非风扇实测范围。',
    'Preview of the PWM points; editing them keeps the BIOS\'s PWM/RPM mode. The graph does not confirm fan routing or the physical response.': 'PWM 点预览；编辑不改变 BIOS 的 PWM/RPM 模式。图形不代表已确认风扇通道或实际响应。',
    'Temperatures for the three curve points, in ': '三个曲线点的温度，单位 ',
    'C. Values must increase down the column.': 'C；沿列数值须递增。',
    'The snapshot requires an absent ordinary power request.': '该快照需要一个缺失的普通功率请求。',
    'The ordinary power request is absent and cannot be restored exactly.': '普通功率请求缺失，无法精确恢复。',
    'Unsupported or ambiguous legacy V/F program.': '旧式 V/F 程序不受支持或存在歧义。',
    'Invalid legacy memory V/F program range.': '旧式显存 V/F 程序范围无效。',
    'Legacy V/F point ownership or type is inconsistent.': '旧式 V/F 点归属或类型不一致。',
    'Invalid or ambiguous legacy V/F point range.': '旧式 V/F 点范围无效或存在歧义。',
    'Memory V/F point has no valid model coordinates.': '显存 V/F 点没有有效模型坐标。',
    'Memory V/F point is not frequency-defined.': '显存 V/F 点未按频率定义。',
    'Legacy V/F point has no unique program owner.': '旧式 V/F 点没有唯一程序归属。',
    'Legacy V/F program has no unique clock owner.': '旧式 V/F 程序没有唯一频率归属。',
    'Unsupported legacy memory V/F response layout.': '不支持旧式显存 V/F 响应布局。',
    'Unsupported legacy memory V/F program geometry.': '不支持旧式显存 V/F 程序结构。',
    'Legacy memory V/F point selections are inconsistent.': '旧式显存 V/F 点选择不一致。',
    'Unsupported legacy memory V/F clock record.': '不支持旧式显存 V/F 频率记录。',
    'Legacy memory V/F clock identity is ambiguous.': '旧式显存 V/F 频率标识不明确。',
    'Legacy profile fan overrides must contain exactly three values.': '旧式配置方案的风扇覆盖值必须恰好有三个。',
    'Profile V/F curves must contain a supported Core point count.': '配置方案 V/F 曲线的核心点数必须受支持。',
    'Thermal limit needs policy 0, type 4, channel 1 and four raw thresholds.': '温度上限需要策略 0、类型 4、通道 1 和四个原始阈值。',
    'Ordinary power-request absence requires the v13 document schema.': '普通功率请求缺失需要 v13 文档结构。',
    'The legacy fan getter changed its buffer guards.': '旧式风扇读取接口的缓冲区保护已变化。',
    'Legacy fan read failed (NVAPI ': '旧式风扇读取失败（NVAPI ',
    'Legacy fan write failed (NVAPI ': '旧式风扇写入失败（NVAPI ',
    'Legacy fan control is unavailable or owned by another instance.': '旧式风扇控制不可用或由其他实例占用。',
    'The legacy fan tachometer read failed validation.': '旧式风扇转速读取未通过验证。',
    'The fan lease GPU identity is missing.': '风扇控制记录缺少 GPU 标识。',
    'An absent ordinary power request cannot be restored exactly.': '缺失的普通功率请求无法精确恢复。',
    'The power-request identity or bounds changed during ': '功率请求标识或边界在',
    'Power-request records changed during readback.': '回读时功率请求记录已变化。',
    'Power-request record identity changed.': '功率请求记录标识已变化。',
    'Single-policy board-power records do not match.': '单策略整卡功率记录不匹配。',
    'Single-policy board-power identities are unavailable.': '单策略整卡功率标识不可用。',
    'GPU fan speed is outside the supported numeric range.': 'GPU 风扇转速超出支持的数值范围。',
    'GPU fan speeds need three coordinates.': 'GPU 风扇转速需要三个坐标。',
    'No memory V/F model points are available.': '没有可用的显存 V/F 模型点。',
    'Current memory clock is unavailable.': '当前显存频率不可用。',
    'The original or active Speedo could not be verified.': '无法验证原始或生效的 Speedo。',
    'Speedo can be edited after the BIOS is active.': 'BIOS 生效后可编辑 Speedo。',
    'No theoretical maximum is known for this offset.': '此偏移没有已知的理论上限。',
    'The Core V/F layout changed; reload the curve before editing.': '核心 V/F 布局已变化；请重新载入曲线。',
    'The profile V/F curve does not match the live Core curve layout.': '配置方案 V/F 曲线与当前核心曲线布局不匹配。',
    'The profile V/F point count does not match this GPU.': '配置方案 V/F 点数与此 GPU 不匹配。',
    'Enter valid curve points before changing policy.': '更改策略前请输入有效曲线点。',
    'Fan policy coordinates exceed the supported numeric range.': '风扇策略坐标超出支持的数值范围。',
}

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
        if i == offset:
            continue
        word = int.from_bytes(data[i:i + 4], 'little')
        total = (total & 0xffffffff) + word + (total >> 32)
        total = (total & 0xffffffff) + (total >> 32)
    total = (total & 0xffff) + (total >> 16)
    total = total + (total >> 16)
    return (total & 0xffff) + len(data)

def main():
    for data, expected in ((old, OLD_SHA256), (zh, OLD_ZH_SHA256), (new, SOURCE_SHA256)):
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('source hash mismatch')
    if sealed_digest(new) != new[seal_positions(new)[1]:seal_positions(new)[1] + 32]:
        raise ValueError('original seal mismatch')
    legacy = {text: values[0][3] for text, values in old_by_text.items()}
    if any(values[0][3] != row[3] for values in old_by_text.values() for row in values):
        raise ValueError('ambiguous legacy translations')
    translations = {**legacy, **CORRECTIONS, **NEW_TRANSLATIONS}
    output = bytearray(new)
    changed = []
    for pos, va, english in strings(new):
        chinese = translations.get(english)
        if not chinese or chinese == english:
            continue
        if pos >= 2 and 0x20 <= new[pos-1] <= 0x7e and 0x20 <= new[pos-2] <= 0x7e:
            continue
        before = english.encode('utf-16le')
        after = chinese.encode('utf-16le')
        if len(after) > len(before):
            continue
        terminated = new[pos + len(before):pos + len(before) + 2] == b'\0\0'
        pad = bytes(len(before) - len(after)) if terminated else ' '.encode('utf-16le') * ((len(before) - len(after)) // 2)
        output[pos:pos + len(before)] = after + pad
        changed.append({'offset': hex(pos), 'va': hex(va), 'english': english, 'chinese': chinese,
                        'source': 'new_review' if english in NEW_TRANSLATIONS or english in CORRECTIONS else 'v0.50.2_review',
                        'embedded_prefix': not terminated})
    checksum, digest = seal_positions(output)
    output[digest:digest + 32] = sealed_digest(output)
    struct.pack_into('<I', output, checksum, pe_checksum(output, checksum))
    if sealed_digest(output) != output[digest:digest + 32]:
        raise ValueError('output seal mismatch')
    if struct.unpack_from('<I', output, checksum)[0] != pe_checksum(output, checksum):
        raise ValueError('checksum mismatch')
    allowed = bytearray(len(new))
    for row in changed:
        pos = int(row['offset'], 16)
        allowed[pos:pos + len(row['english'].encode('utf-16le'))] = bytes([1]) * len(row['english'].encode('utf-16le'))
    allowed[digest:digest + 32] = bytes([1]) * 32
    allowed[checksum:checksum + 4] = bytes([1]) * 4
    if any(a != b and not allowed[i] for i, (a,b) in enumerate(zip(new, output))):
        raise ValueError('change outside approved ranges')
    OUTPUT.write_bytes(output)
    MANIFEST.write_text(json.dumps({'source_sha256': SOURCE_SHA256,
        'output_sha256': hashlib.sha256(output).hexdigest(), 'translation_count': len(changed),
        'file_size': len(output), 'translated': changed}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(changed)} translations; {OUTPUT}; SHA256 {hashlib.sha256(output).hexdigest()}')

if __name__ == '__main__':
    main()
