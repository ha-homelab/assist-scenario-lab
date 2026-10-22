# 記録済み音声シナリオの評価

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

## インストールと境界

チェックアウトしたソースから、仮想環境内で `python3 -m pip install .` を実行してインストールします。Python 3.11+ に対応しています。Python 以外の実行時依存関係はありません。`assist-lab --help --lang en` でコマンド一覧を表示できます。`ru`、`de`、`es` も使用できます。モジュールの起動方法は `python3 -m assist_scenario_lab` です。

ファイル読み込みには Linux と macOS が提供する OS フラグ `O_NOFOLLOW` と `O_NONBLOCK` が必要です。どちらかがなければ、CLI は入力を開く前に `unsupported_platform` と終了コード 2 を返します。メモリ内での評価・インポートを行う Python API には、これらのフラグは不要です。

これはオフライン評価ツールであり、サテライトのファームウェア、音響検出器、ライブ収集ツール、HA 統合、完全なベンチマークではありません。実際の製品のユーザー受け入れテストは適切なファームウェア用ツールで実施してください。その結果の範囲を限定した証拠は、プライバシーを確認してから本ツールに渡してください。

## 正規入力

`examples/synthetic-pass.json` から始めます。ルートには `schema: assist-scenario-lab/v1`、真偽値の `synthetic`、`requirements` オブジェクト、1～500 件の `sessions` が必要です。不明なフィールドは拒否します。セッションは一意の `id` と `platform`、`scenario`、`clock`、`events`、`checks` を持ちます。ID は 1～64 文字の ASCII 英字、数字、アンダースコア、ハイフンで構成し、英字か数字で始めます。部屋名、住所、機器識別子ではなく仮名を使ってください。

`clock` は `relative_monotonic` または `utc_derived` です。イベントには `stage`、`at_ms`、`origin` を含めます。時刻は有限かつ非負、最大 12 時間で、非減少順とします。最初のイベントは時刻ゼロの `request` です。各ステージは 1 回だけ出現します。対応ステージは `request`、`wake_detected`、`stt_end`、`intent_end`、`tts_ready`、`protocol_end`、`playback_started`、`playback_finished`、`audible_start`、`error` です。パイプラインによってはストリーミングを行うため、タイムスタンプの時系列順以外には TTS と再生の固定順を意図的に設けていません。

発生元は `pipeline`、`satellite`、`operator`、`acoustic` です。`audible_start` の発生元になれるのは `operator` または `acoustic` だけです。各セッションは `intent_correct`、`action_observed`、`audible` の 3 検査をすべて提供する必要があります。各検査は `result`（`pass`、`fail`、`unknown`）と `method` を持ちます。不明な結果には `none` が必要です。それ以外の有効な方法は、意図に `operator`/`intent_assertion`、動作に `operator`/`ha_state`、可聴性に `operator`/`acoustic` です。可聴時刻のタイムスタンプには可聴性検査の合格が必要です。ツールが検証するのは整合性であり、事実性ではありません。

要件では 3 検査のいずれも有効にでき、任意で `max_audible_ms` を設定できます。省略した検査や false の検査は必須ではありません。API のみのポリシーは物理的証拠がなくても合格でき、その旨を明記する必要があります。同梱例はすべての検査を必須とします。パイプラインエラーは常に不合格です。`protocol_end` の欠如は不完全を意味します。必須項目の不合格は不明な観測より優先されます。遅延がしきい値を超えれば不合格、必須の遅延値がなければ不完全です。

## HA 実行のインポート

アダプターが受け取るのは 1 つの**イベントオブジェクトの配列**であり、WebSocket ログ全体や診断 ZIP ではありません。各イベントの本体をローカルで取り出してください。オブジェクトのフィールドは厳密に `type`、`timestamp`、`data` です。データはオブジェクトまたは null にできます。タイムスタンプにはタイムゾーン付き ISO 8601 を使います。`run-start` で始め、時系列順を守り、複数の実行を混ぜないでください。対応付けられたステージの重複は拒否します。

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

2 番目のコマンドは意図的に 3 を返します。`run-end` は `protocol_end` になり、物理的成功にはなりません。`tts-end` は `tts_ready` になり、可聴音にはなりません。文字起こし、入力テキスト、エラー、TTS の URL/トークン、パイプラインメタデータを含むすべての `data` を破棄します。開始、進捗、VAD イベントは認識しますが保存しません。変換後の時刻は `utc_derived` を使います。実時刻の減算は単調な遅延測定ではなく、時計補正の影響を受けます。3 つの物理的・意味的検査はいずれも不明のままです。

## レポートと比較

`--format text|json|html|junit` でレポートを選びます。シェルのリダイレクトで結果を指定したローカルパスに書き込みます。CLI 自体が入力を上書きすることはありません。終了コードは 0 が記録された要件に合格、1 が不合格、2 が不正な入力・引数、3 が不完全です。JUnit は不完全なセッションをスキップとして表しますが、CI は終了コード 3 を引き続き考慮する必要があります。

JSON のグループはプラットフォーム、シナリオ、時計、可聴時刻の測定方法の組み合わせです。異なる時計や、人による観測と音響的観測を、交換可能な測定として比較してはいけません。p50/p95 は最近傍順位法を使います。20 標本未満では p95 は null です。20 は報告のしきい値であり、統計的信頼性の証拠ではありません。音声を観測した不合格セッションも遅延の標本集団に残り、不合格数も表示し続けます。合格した試行だけを選ばないでください。生音声や文字起こしは出力しません。ID から情報が漏れる可能性はあるので確認してください。

HTML は全セッションを一覧にし、最初の 50 件の可聴観測を共通の尺度で描画します。各行のプラットフォームと方法を確認してください。概要は統計的な順位表ではありません。`evidence_verified: false` は常に存在します。`synthetic: false` は作成者が実行を合成と印付けしなかったという意味で、ハードウェアが独立に検証されたという意味ではありません。

## 意味のある証拠を収集する

試行前に期待する意図と対象を定義します。開始イベントは一貫して指定してください。パイプライン要求が発話の開始とは限りません。ソフトウェアのバージョン、言語、ネットワーク条件、マイクとスピーカーの位置、観測方法、試行数を外部の試験記録に残してください。精密な可聴時刻には適切な音響測定を使い、最初のネットワーク断片で代用しないでください。不合格、タイムアウト、証拠の欠如も記録します。本パッケージは音響同期や同意の管理を行いません。

## トラブルシューティング

- `object_fields`：正規 fixture のキーと比較してください。診断ダンプ全体は受け付けません。
- `ha_timestamp` / `time_order`：1 実行だけをエクスポートし、タイムゾーンを含め、時計補正を確認します。遅延を作り出すためにイベントの順序を変えないでください。
- `stage`：不明または重複したステージです。2 実行を結合していないか確認します。
- `audible_origin` / `conflicting_audible`：再生メタデータは音を聞いた事実の代わりにはなりません。
- API 成功後の終了コード 3：必要な観測が記録されるまでは正常な挙動です。
- `unsupported_platform`：OS に `O_NOFOLLOW` または `O_NONBLOCK` がありません。両方を備えた環境（Linux または macOS）を使ってください。シンボリックリンクや FIFO 検査を弱めるのではなく、開く前に入力を拒否します。
- `file_size_type`：通常の UTF-8 JSON ファイルのみ、最大 2 MiB です。ディレクトリ、FIFO、最終パス要素のシンボリックリンクは拒否します。親ディレクトリのリンクはサンドボックス境界ではありません。
- `number`：負、非有限、真偽値、12 時間超のタイムスタンプは使えません。

エラーでは翻訳した概要と安定したコードを出力し、元の内容やローカルパスは出力しません。公開例はすべて合成です。エクスポートはこのチェックアウトの外、できれば非公開の一時ディレクトリに保存してください。

## アーキテクチャ、翻訳、出典

![オフラインの流れ](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` が純粋な検証、インポート、評価を担当し、`cli.py` が各形式を生成します。`locales/*.json` には 4 つのカタログがあります。テストではカタログキーの一致を要求します。機械用キーと診断コードは翻訳しません。完全なガイドは ha-homelab の 24 文書言語をカバーし、CLI と README は英語、ロシア語、ドイツ語、スペイン語のままです。一致検査とレビュー済みの例を伴う参照翻訳の追加を歓迎します。

プロトコルの対応は [Home Assistant Assist 文書](https://developers.home-assistant.io/docs/voice/pipelines/)と [HA 2026.10.0 のイベントモデル](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py)で確認しました。サテライトのライフサイクルは[公式エンティティガイド](https://developers.home-assistant.io/docs/core/entity/assist-satellite/)に記載されています。これらの上流 API は音響検証を約束していません。ここで分離するのは設計上の判断です。
