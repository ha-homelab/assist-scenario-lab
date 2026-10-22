# 評估記錄的語音場景

<!-- language-navigation:start -->
<p dir="ltr">
<a href="../en/guide.md" lang="en" dir="ltr">English</a> ·
<a href="../ar/guide.md" lang="ar" dir="rtl">العربية</a> ·
<a href="../bn/guide.md" lang="bn" dir="ltr">বাংলা</a> ·
<a href="../cs/guide.md" lang="cs" dir="ltr">Čeština</a> ·
<a href="../de/guide.md" lang="de" dir="ltr">Deutsch</a> ·
<a href="../es/guide.md" lang="es" dir="ltr">Español</a> ·
<a href="../fa/guide.md" lang="fa" dir="rtl">فارسی</a> ·
<a href="../fr/guide.md" lang="fr" dir="ltr">Français</a> ·
<a href="../he/guide.md" lang="he" dir="rtl">עברית</a> ·
<a href="../hi/guide.md" lang="hi" dir="ltr">हिन्दी</a> ·
<a href="../id/guide.md" lang="id" dir="ltr">Bahasa Indonesia</a> ·
<a href="../it/guide.md" lang="it" dir="ltr">Italiano</a> ·
<a href="../ja/guide.md" lang="ja" dir="ltr">日本語</a> ·
<a href="../ko/guide.md" lang="ko" dir="ltr">한국어</a> ·
<a href="../nl/guide.md" lang="nl" dir="ltr">Nederlands</a> ·
<a href="../pl/guide.md" lang="pl" dir="ltr">Polski</a> ·
<a href="../pt/guide.md" lang="pt" dir="ltr">Português</a> ·
<a href="../ru/guide.md" lang="ru" dir="ltr">Русский</a> ·
<a href="../th/guide.md" lang="th" dir="ltr">ไทย</a> ·
<a href="../tr/guide.md" lang="tr" dir="ltr">Türkçe</a> ·
<a href="../uk/guide.md" lang="uk" dir="ltr">Українська</a> ·
<a href="../vi/guide.md" lang="vi" dir="ltr">Tiếng Việt</a> ·
<a href="../zh-Hans/guide.md" lang="zh-Hans" dir="ltr">简体中文</a> ·
<a href="../zh-Hant/guide.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

## 安裝與邊界

在虛擬環境中，從檢出的程式碼透過 `python3 -m pip install .` 安裝。支援 Python 3.11+。除 Python 外沒有執行期相依套件。`assist-lab --help --lang en` 列出命令；`ru`、`de` 和 `es` 也可使用。模組入口是 `python3 -m assist_scenario_lab`。

載入檔案需要作業系統的 `O_NOFOLLOW` 和 `O_NONBLOCK` 標誌，Linux 和 macOS 均提供。缺少任意一個時，CLI 會在開啟輸入前以退出碼 2 返回 `unsupported_platform`。在記憶體中評估和匯入資料的 Python API 不需要這些標誌。

這是離線評估器，不是衛星裝置韌體、聲學檢測器、即時收集器、HA 整合或完整基準測試。請使用適當的韌體工具進行真正的產品使用者驗收測試。先審查隱私，再將得到的有限範圍證據提供給本工具。

## 規範輸入

從 `examples/synthetic-pass.json` 開始。根物件必須包含 `schema: assist-scenario-lab/v1`、布林值 `synthetic`、`requirements` 物件和 1–500 個 `sessions`。未知欄位會被拒絕。工作階段包含唯一的 `id`，以及 `platform`、`scenario`、`clock`、`events` 和 `checks`。ID 由 1–64 個 ASCII 字母、數字、底線或連字元組成，首字元為字母或數字。請使用化名，不要使用房間名稱、地址或裝置識別符號。

`clock` 為 `relative_monotonic` 或 `utc_derived`。事件包含 `stage`、`at_ms`、`origin`。時間必須有限、非負、不超過 12 小時，並按非遞減順序排列。第一個事件是零時刻的 `request`。每個階段只能出現一次。支援的階段：`request`、`wake_detected`、`stt_end`、`intent_end`、`tts_ready`、`protocol_end`、`playback_started`、`playback_finished`、`audible_start`、`error`。不同管線可以流式處理；因此除時間戳記的先後順序外，工具有意不規定 TTS 與播放的固定順序。

來源為 `pipeline`、`satellite`、`operator` 和 `acoustic`。只有 `operator` 或 `acoustic` 能作為 `audible_start` 的來源。每個工作階段必須提供全部三項檢查：`intent_correct`、`action_observed`、`audible`。每項都有 `result`（`pass`、`fail`、`unknown`）和 `method`。未知結果必須使用 `none`。其他有效方法為：意圖使用 `operator`/`intent_assertion`，動作使用 `operator`/`ha_state`，可聽性使用 `operator`/`acoustic`。可聽時間戳記要求可聽性檢查通過。工具驗證一致性，而非真實性。

要求可以啟用三項檢查中的任何一項，並可選設定 `max_audible_ms`。省略或為 false 的檢查不是必需項：僅檢查 API 的策略可以在沒有物理證據時通過，必須明確標註。附帶範例要求全部檢查。管線錯誤總會導致失敗。缺少 `protocol_end` 表示不完整。必需項失敗優先於未知觀察結果。延遲超過門檻即失敗；缺少必需的延遲資料則為不完整。

## 匯入 HA 執行記錄

轉接器接收一個**事件物件陣列**，不是完整 WebSocket 日誌或診斷 ZIP。請在本機提取每個事件的內容。物件必須恰好包含 `type`、`timestamp`、`data`；資料可以是物件或 null。時間戳記必須為帶時區的 ISO 8601。以 `run-start` 開始，保留時間順序，不要混合不同執行。重複的對應階段會被拒絕。

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

第二條命令有意返回 3。`run-end` 對應為 `protocol_end`，而非物理成功。`tts-end` 對應為 `tts_ready`，而非可聽聲音。所有 `data` 都會被丟棄，包括轉錄、輸入文字、錯誤、TTS URL/權杖和管線後設資料。開始、進度及 VAD 事件可被識別，但不保留。轉換後的時間使用 `utc_derived`：實際時鐘相減不是單調延遲測量，並會受時鐘調整影響。三項物理/語義檢查全部保持未知。

## 報告與比較

`--format text|json|html|junit` 選擇報告格式。Shell 重新導向將結果寫入選定的本機路徑。CLI 本身從不覆蓋輸入。退出碼：0 表示記錄的要求通過；1 為失敗；2 為無效輸入/引數；3 為不完整。JUnit 將不完整工作階段表示為跳過；CI 仍須遵守退出碼 3。

JSON 按平台、場景、時鐘和可聽時間測量方法分組。絕不要將不同的時鐘，或人工觀察與聲學觀察，當作可互換的測量。p50/p95 使用最近秩法。少於 20 個樣本時 p95 為 null；20 是報告門檻，不是統計信賴度的證據。觀察到音訊的失敗工作階段仍納入延遲樣本總體，失敗計數也仍然可見。不要只挑選通過的試驗。不匯出原始音訊或轉錄。ID 仍可能洩露資訊，請審查。

HTML 列出全部工作階段，並用統一尺度繪製前 50 個可聽觀察結果。請閱讀每行的平台和方法；概覽不是統計排名。始終包含 `evidence_verified: false`。`synthetic: false` 表示作者未將該執行標示為合成資料，並不意味著硬體經過獨立驗證。

## 收集有意義的證據

試驗前定義預期意圖和目標。一致地定義開始事件：管線請求不一定是說話開始的時刻。另行記錄試驗日誌，包含軟體版本、語言、網路條件、麥克風和揚聲器位置、觀察方法及試驗次數。精確測量可聽時間應採用適當聲學測量，不要以第一個網路資料塊代替。記錄失敗、逾時和缺失證據。本套件不執行聲學同步或同意管理。

## 故障排查

- `object_fields`：對照規範 fixture 檢查鍵；不接受完整診斷傾印。
- `ha_timestamp` / `time_order`：匯出一次執行，包含時區，檢查時鐘修正。不要重新排列事件來人為製造延遲。
- `stage`：階段未知或重複；檢查是否拼接了兩次執行。
- `audible_origin` / `conflicting_audible`：播放後設資料不能代替聽到聲音。
- API 成功後退出碼為 3：在記錄必需的觀察結果之前，這是預期行為。
- `unsupported_platform`：作業系統缺少 `O_NOFOLLOW` 或 `O_NONBLOCK`；使用同時提供兩者的環境（Linux 或 macOS）。工具在開啟輸入前拒絕，而不會放鬆符號連結或 FIFO 檢查。
- `file_size_type`：只接受普通 UTF-8 JSON 檔案，最大 2 MiB。目錄、FIFO 和路徑最後一部分的符號連結會被拒絕。父目錄中的符號連結不構成沙箱邊界。
- `number`：時間戳記不得為負數、非有限數、布林值，也不得超過 12 小時。

錯誤只輸出翻譯後的摘要和穩定代碼，不輸出來源內容或本機路徑。公開範例完全是合成資料。請將匯出檔案放在此工作副本之外，最好置於私人暫存目錄。

## 架構、翻譯與來源

![離線流程](../../assets/architecture.svg)

`core.py` 負責純驗證、匯入和評估；`cli.py` 產生各種格式；`locales/*.json` 包含四套語言目錄。測試要求目錄鍵完全一致。機器鍵和診斷代碼不翻譯。完整指南涵蓋 ha-homelab 的 24 種文件語言；CLI 與 README 仍為英語、俄語、德語和西班牙語。歡迎貢獻其他參考翻譯，並提供一致性測試和審查過的範例。

協議對應已對照 [Home Assistant Assist 文件](https://developers.home-assistant.io/docs/voice/pipelines/)和 [HA 2026.10.0 事件模型](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py)核查。衛星裝置生命週期見[官方實體指南](https://developers.home-assistant.io/docs/core/entity/assist-satellite/)。這些上游 API 不承諾聲學驗證；在這裡將兩者分開是設計決策。
