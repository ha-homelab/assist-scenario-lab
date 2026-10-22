# 评估记录的语音场景

<!-- language-navigation:start -->
<p dir="ltr">
<a href="Guide.md" lang="en" dir="ltr">English</a> ·
<a href="Guide-ar.md" lang="ar" dir="rtl">العربية</a> ·
<a href="Guide-bn.md" lang="bn" dir="ltr">বাংলা</a> ·
<a href="Guide-cs.md" lang="cs" dir="ltr">Čeština</a> ·
<a href="Guide-de.md" lang="de" dir="ltr">Deutsch</a> ·
<a href="Guide-es.md" lang="es" dir="ltr">Español</a> ·
<a href="Guide-fa.md" lang="fa" dir="rtl">فارسی</a> ·
<a href="Guide-fr.md" lang="fr" dir="ltr">Français</a> ·
<a href="Guide-he.md" lang="he" dir="rtl">עברית</a> ·
<a href="Guide-hi.md" lang="hi" dir="ltr">हिन्दी</a> ·
<a href="Guide-id.md" lang="id" dir="ltr">Bahasa Indonesia</a> ·
<a href="Guide-it.md" lang="it" dir="ltr">Italiano</a> ·
<a href="Guide-ja.md" lang="ja" dir="ltr">日本語</a> ·
<a href="Guide-ko.md" lang="ko" dir="ltr">한국어</a> ·
<a href="Guide-nl.md" lang="nl" dir="ltr">Nederlands</a> ·
<a href="Guide-pl.md" lang="pl" dir="ltr">Polski</a> ·
<a href="Guide-pt.md" lang="pt" dir="ltr">Português</a> ·
<a href="Guide-RU.md" lang="ru" dir="ltr">Русский</a> ·
<a href="Guide-th.md" lang="th" dir="ltr">ไทย</a> ·
<a href="Guide-tr.md" lang="tr" dir="ltr">Türkçe</a> ·
<a href="Guide-uk.md" lang="uk" dir="ltr">Українська</a> ·
<a href="Guide-vi.md" lang="vi" dir="ltr">Tiếng Việt</a> ·
<a href="Guide-zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> ·
<a href="Guide-zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

## 安装与边界

在虚拟环境中，从检出的代码通过 `python3 -m pip install .` 安装。支持 Python 3.11+。除 Python 外没有运行时依赖。`assist-lab --help --lang en` 列出命令；`ru`、`de` 和 `es` 也可使用。模块入口是 `python3 -m assist_scenario_lab`。

加载文件需要操作系统的 `O_NOFOLLOW` 和 `O_NONBLOCK` 标志，Linux 和 macOS 均提供。缺少任意一个时，CLI 会在打开输入前以退出码 2 返回 `unsupported_platform`。在内存中评估和导入数据的 Python API 不需要这些标志。

这是离线评估器，不是卫星设备固件、声学检测器、实时采集器、HA 集成或完整基准测试。请使用适当的固件工具进行真正的产品用户验收测试。先审查隐私，再将得到的有限范围证据提供给本工具。

## 规范输入

从 `examples/synthetic-pass.json` 开始。根对象必须包含 `schema: assist-scenario-lab/v1`、布尔值 `synthetic`、`requirements` 对象和 1–500 个 `sessions`。未知字段会被拒绝。会话包含唯一的 `id`，以及 `platform`、`scenario`、`clock`、`events` 和 `checks`。ID 由 1–64 个 ASCII 字母、数字、下划线或连字符组成，首字符为字母或数字。请使用化名，不要使用房间名称、地址或设备标识符。

`clock` 为 `relative_monotonic` 或 `utc_derived`。事件包含 `stage`、`at_ms`、`origin`。时间必须有限、非负、不超过 12 小时，并按非递减顺序排列。第一个事件是零时刻的 `request`。每个阶段只能出现一次。支持的阶段：`request`、`wake_detected`、`stt_end`、`intent_end`、`tts_ready`、`protocol_end`、`playback_started`、`playback_finished`、`audible_start`、`error`。不同流水线可以流式处理；因此除时间戳的先后顺序外，工具有意不规定 TTS 与播放的固定顺序。

来源为 `pipeline`、`satellite`、`operator` 和 `acoustic`。只有 `operator` 或 `acoustic` 能作为 `audible_start` 的来源。每个会话必须提供全部三项检查：`intent_correct`、`action_observed`、`audible`。每项都有 `result`（`pass`、`fail`、`unknown`）和 `method`。未知结果必须使用 `none`。其他有效方法为：意图使用 `operator`/`intent_assertion`，动作使用 `operator`/`ha_state`，可听性使用 `operator`/`acoustic`。可听时间戳要求可听性检查通过。工具验证一致性，而非真实性。

要求可以启用三项检查中的任何一项，并可选设定 `max_audible_ms`。省略或为 false 的检查不是必需项：仅检查 API 的策略可以在没有物理证据时通过，必须明确标注。附带示例要求全部检查。流水线错误总会导致失败。缺少 `protocol_end` 表示不完整。必需项失败优先于未知观察结果。延迟超过阈值即失败；缺少必需的延迟数据则为不完整。

## 导入 HA 运行记录

适配器接收一个**事件对象数组**，不是完整 WebSocket 日志或诊断 ZIP。请在本地提取每个事件的内容。对象必须恰好包含 `type`、`timestamp`、`data`；数据可以是对象或 null。时间戳必须为带时区的 ISO 8601。以 `run-start` 开始，保留时间顺序，不要混合不同运行。重复的映射阶段会被拒绝。

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

第二条命令有意返回 3。`run-end` 映射为 `protocol_end`，而非物理成功。`tts-end` 映射为 `tts_ready`，而非可听声音。所有 `data` 都会被丢弃，包括转录、输入文本、错误、TTS URL/令牌和流水线元数据。开始、进度及 VAD 事件可被识别，但不保留。转换后的时间使用 `utc_derived`：墙上时钟相减不是单调延迟测量，并会受时钟调整影响。三项物理/语义检查全部保持未知。

## 报告与比较

`--format text|json|html|junit` 选择报告格式。Shell 重定向将结果写入选定的本地路径。CLI 本身从不覆盖输入。退出码：0 表示记录的要求通过；1 为失败；2 为无效输入/参数；3 为不完整。JUnit 将不完整会话表示为跳过；CI 仍须遵守退出码 3。

JSON 按平台、场景、时钟和可听时间测量方法分组。绝不要将不同的时钟，或人工观察与声学观察，当作可互换的测量。p50/p95 使用最近秩法。少于 20 个样本时 p95 为 null；20 是报告阈值，不是统计置信度的证据。观察到音频的失败会话仍纳入延迟样本总体，失败计数也仍然可见。不要只挑选通过的试验。不导出原始音频或转录。ID 仍可能泄露信息，请审查。

HTML 列出全部会话，并用统一尺度绘制前 50 个可听观察结果。请阅读每行的平台和方法；概览不是统计排名。始终包含 `evidence_verified: false`。`synthetic: false` 表示作者未将该运行标为合成数据，并不意味着硬件经过独立验证。

## 收集有意义的证据

试验前定义预期意图和目标。一致地定义开始事件：流水线请求不一定是说话开始的时刻。另行记录试验日志，包含软件版本、语言、网络条件、麦克风和扬声器位置、观察方法及试验次数。精确测量可听时间应采用适当声学测量，不要以第一个网络数据块代替。记录失败、超时和缺失证据。本包不执行声学同步或同意管理。

## 故障排查

- `object_fields`：对照规范 fixture 检查键；不接受完整诊断转储。
- `ha_timestamp` / `time_order`：导出一次运行，包含时区，检查时钟修正。不要重新排列事件来人为制造延迟。
- `stage`：阶段未知或重复；检查是否拼接了两次运行。
- `audible_origin` / `conflicting_audible`：播放元数据不能代替听到声音。
- API 成功后退出码为 3：在记录必需的观察结果之前，这是预期行为。
- `unsupported_platform`：操作系统缺少 `O_NOFOLLOW` 或 `O_NONBLOCK`；使用同时提供两者的环境（Linux 或 macOS）。工具在打开输入前拒绝，而不会放松符号链接或 FIFO 检查。
- `file_size_type`：只接受普通 UTF-8 JSON 文件，最大 2 MiB。目录、FIFO 和路径最后一部分的符号链接会被拒绝。父目录中的符号链接不构成沙箱边界。
- `number`：时间戳不得为负数、非有限数、布尔值，也不得超过 12 小时。

错误只输出翻译后的摘要和稳定代码，不输出源内容或本地路径。公开示例完全是合成数据。请将导出文件放在此工作副本之外，最好置于私有临时目录。

## 架构、翻译与来源

![离线流程](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` 负责纯验证、导入和评估；`cli.py` 渲染各种格式；`locales/*.json` 包含四套语言目录。测试要求目录键完全一致。机器键和诊断代码不翻译。完整指南涵盖 ha-homelab 的 24 种文档语言；CLI 与 README 仍为英语、俄语、德语和西班牙语。欢迎贡献其他参考翻译，并提供一致性测试和审查过的示例。

协议映射已对照 [Home Assistant Assist 文档](https://developers.home-assistant.io/docs/voice/pipelines/)和 [HA 2026.10.0 事件模型](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py)核查。卫星设备生命周期见[官方实体指南](https://developers.home-assistant.io/docs/core/entity/assist-satellite/)。这些上游 API 不承诺声学验证；在这里将两者分开是设计决策。
