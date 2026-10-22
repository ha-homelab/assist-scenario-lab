# 기록된 음성 시나리오 평가

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

## 설치와 경계

체크아웃한 코드에서 가상 환경 안에 `python3 -m pip install .`로 설치하세요. Python 3.11+를 지원합니다. Python 외에는 런타임 의존성이 없습니다. `assist-lab --help --lang en`은 명령을 나열하며 `ru`, `de`, `es`도 사용할 수 있습니다. 모듈 진입점은 `python3 -m assist_scenario_lab`입니다.

파일을 읽으려면 Linux와 macOS에 있는 OS 플래그 `O_NOFOLLOW`와 `O_NONBLOCK`가 필요합니다. 하나라도 없으면 CLI는 입력을 열기 전에 `unsupported_platform`과 종료 코드 2를 반환합니다. 메모리 내 Python 평가 및 가져오기 API에는 이 플래그가 필요하지 않습니다.

이 도구는 오프라인 평가기이며 위성 기기 펌웨어, 음향 감지기, 실시간 수집기, HA 통합 또는 완전한 벤치마크가 아닙니다. 실제 제품 사용자 인수 테스트는 적절한 펌웨어 도구로 수행하세요. 그 결과로 얻은 제한된 범위의 증거를 이 도구에 넣기 전에 개인정보를 검토하세요.

## 표준 입력

`examples/synthetic-pass.json`에서 시작하세요. 루트에는 `schema: assist-scenario-lab/v1`, 불리언 `synthetic`, `requirements` 객체, 1–500개의 `sessions`가 필요합니다. 알 수 없는 필드는 거부합니다. 세션에는 고유한 `id`와 `platform`, `scenario`, `clock`, `events`, `checks`가 있습니다. ID는 ASCII 문자, 숫자, 밑줄, 하이픈 1–64자로 구성하며 문자나 숫자로 시작합니다. 방 이름, 주소, 기기 식별자 대신 가명을 쓰세요.

`clock`은 `relative_monotonic` 또는 `utc_derived`입니다. 이벤트는 `stage`, `at_ms`, `origin`을 포함합니다. 시간은 유한하고 음수가 아니며 최대 12시간이고 비감소 순서여야 합니다. 첫 이벤트는 시각 0의 `request`입니다. 각 단계는 한 번만 나타납니다. 지원 단계는 `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`입니다. 파이프라인에 따라 스트리밍할 수 있으므로 타임스탬프의 시간순 외에는 TTS와 재생 순서를 의도적으로 고정하지 않습니다.

출처는 `pipeline`, `satellite`, `operator`, `acoustic`입니다. `operator` 또는 `acoustic`만 `audible_start`의 출처가 될 수 있습니다. 모든 세션은 `intent_correct`, `action_observed`, `audible`의 세 검사를 모두 제공해야 합니다. 각 검사에는 `result`(`pass`, `fail`, `unknown`)와 `method`가 있습니다. 알 수 없는 결과에는 `none`이 필요합니다. 그 밖의 유효한 방법은 의도에 `operator`/`intent_assertion`, 동작에 `operator`/`ha_state`, 가청성에 `operator`/`acoustic`입니다. 소리가 들린 시각의 타임스탬프에는 가청성 검사 통과가 필요합니다. 도구는 일관성을 확인하며 진실 여부를 보증하지 않습니다.

요구사항은 세 검사 중 어느 것이든 활성화하고 선택적으로 `max_audible_ms`를 지정할 수 있습니다. 생략했거나 false인 검사는 필수가 아닙니다. API 전용 정책은 물리적 증거 없이 통과할 수 있으므로 그렇게 표시해야 합니다. 포함된 예제는 모든 검사를 요구합니다. 파이프라인 오류는 항상 실패입니다. `protocol_end`가 없으면 불완전합니다. 필수 검사의 실패가 알 수 없는 관찰보다 우선합니다. 지연이 임계값을 넘으면 실패이고 필수 지연 측정값이 없으면 불완전합니다.

## HA 실행 가져오기

어댑터는 **이벤트 객체 배열** 하나를 받으며 전체 WebSocket 로그나 진단 ZIP은 받지 않습니다. 각 이벤트 본문을 로컬에서 추출하세요. 객체에는 정확히 `type`, `timestamp`, `data`가 있어야 하며 데이터는 객체나 null일 수 있습니다. 타임스탬프는 시간대가 포함된 ISO 8601이어야 합니다. `run-start`로 시작하고 시간순을 유지하며 서로 다른 실행을 섞지 마세요. 매핑된 단계가 중복되면 거부합니다.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

두 번째 명령은 의도적으로 3을 반환합니다. `run-end`는 물리적 성공이 아닌 `protocol_end`로 매핑됩니다. `tts-end`는 들리는 소리가 아닌 `tts_ready`로 매핑됩니다. 전사문, 입력 텍스트, 오류, TTS URL/토큰, 파이프라인 메타데이터를 포함한 모든 `data`를 버립니다. 시작, 진행, VAD 이벤트는 인식하지만 보존하지 않습니다. 변환한 시간은 `utc_derived`를 사용합니다. 실제 시각끼리의 뺄셈은 단조 지연 측정이 아니며 시계 조정에 영향을 받을 수 있습니다. 세 물리적/의미적 검사는 모두 알 수 없는 상태로 남습니다.

## 보고서와 비교

`--format text|json|html|junit`은 보고서를 선택합니다. 셸 리디렉션으로 결과를 선택한 로컬 경로에 씁니다. CLI 자체가 입력을 덮어쓰지는 않습니다. 종료 코드는 0이 기록된 요구사항 통과, 1이 실패, 2가 잘못된 입력/인수, 3이 불완전입니다. JUnit은 불완전한 세션을 건너뜀으로 표현하지만 CI는 여전히 종료 코드 3을 반영해야 합니다.

JSON은 플랫폼 + 시나리오 + 시계 + 가청 시각 측정 방법으로 그룹화합니다. 서로 다른 시계나 사람의 관찰과 음향 관찰을 대체 가능한 측정값으로 비교하지 마세요. p50/p95는 최근접 순위 방법을 사용합니다. 표본이 20개 미만이면 p95는 null입니다. 20은 보고 임계값이지 통계적 신뢰도의 증거가 아닙니다. 소리가 관찰된 실패 세션도 지연 표본 집단에 남고 실패 횟수도 계속 표시됩니다. 통과한 시도만 골라내지 마세요. 원본 오디오나 전사문은 내보내지 않습니다. ID는 여전히 정보를 노출할 수 있으니 검토하세요.

HTML은 모든 세션을 나열하고 처음 50개의 가청 관찰을 공통 축척으로 그립니다. 각 행의 플랫폼과 방법을 확인하세요. 개요는 통계 순위가 아닙니다. `evidence_verified: false`는 항상 존재합니다. `synthetic: false`는 작성자가 실행을 합성으로 표시하지 않았다는 뜻이지 하드웨어가 독립적으로 검증됐다는 뜻이 아닙니다.

## 의미 있는 증거 수집

시도 전에 예상 의도와 대상을 정의하세요. 시작 이벤트를 일관되게 지정하세요. 파이프라인 요청 시점이 발화 시작 시점과 같지는 않을 수 있습니다. 소프트웨어 버전, 언어, 네트워크 조건, 마이크와 스피커 위치, 관찰 방법, 시도 횟수를 별도 실험 기록으로 남기세요. 정확한 가청 시각에는 적절한 음향 측정을 사용하고 첫 네트워크 조각으로 대체하지 마세요. 실패, 시간 초과, 누락된 증거를 기록하세요. 이 패키지는 음향 동기화나 동의 관리를 수행하지 않습니다.

## 문제 해결

- `object_fields`: 키를 표준 fixture와 비교하세요. 전체 진단 덤프는 허용하지 않습니다.
- `ha_timestamp` / `time_order`: 실행 하나를 내보내고 시간대를 포함하며 시계 보정을 확인하세요. 지연을 만들어 내려고 이벤트 순서를 바꾸지 마세요.
- `stage`: 알 수 없거나 중복된 단계입니다. 두 실행을 이어 붙였는지 확인하세요.
- `audible_origin` / `conflicting_audible`: 재생 메타데이터는 실제로 소리를 듣는 것을 대신하지 못합니다.
- API 성공 뒤 종료 코드 3: 필수 관찰이 기록되기 전까지는 예상되는 결과입니다.
- `unsupported_platform`: OS에 `O_NOFOLLOW` 또는 `O_NONBLOCK`가 없습니다. 둘 다 제공하는 환경인 Linux 또는 macOS를 사용하세요. 심볼릭 링크나 FIFO 검사를 약화하는 대신 입력을 열기 전에 거부합니다.
- `file_size_type`: 최대 2 MiB의 일반 UTF-8 JSON 파일만 가능합니다. 디렉터리, FIFO, 마지막 경로 구성요소의 심볼릭 링크는 거부합니다. 부모 디렉터리의 심볼릭 링크는 샌드박스 경계가 아닙니다.
- `number`: 음수, 유한하지 않은 수, 불리언, 12시간을 넘는 타임스탬프는 허용하지 않습니다.

오류는 번역된 요약과 안정적인 코드를 출력하며 원본 내용이나 로컬 경로를 출력하지 않습니다. 공개 예제는 전부 합성 데이터입니다. 내보낸 자료는 이 체크아웃 밖에, 가급적 비공개 임시 디렉터리에 보관하세요.

## 아키텍처, 번역, 출처

![오프라인 흐름](../../assets/architecture.svg)

`core.py`는 순수 검증, 가져오기, 평가를 처리하고 `cli.py`는 출력 형식을 렌더링하며 `locales/*.json`에는 네 카탈로그가 있습니다. 테스트는 카탈로그 키의 일치를 요구합니다. 기계용 키와 진단 코드는 번역하지 않습니다. 전체 가이드는 ha-homelab 문서의 24개 언어를 제공하며 CLI와 README는 영어, 러시아어, 독일어, 스페인어로 유지됩니다. 일치 검사와 검토된 예제를 포함한 추가 참조 번역을 기여하세요.

프로토콜 매핑은 [Home Assistant Assist 문서](https://developers.home-assistant.io/docs/voice/pipelines/)와 [HA 2026.10.0 이벤트 모델](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py)을 기준으로 확인했습니다. 위성 기기 수명 주기는 [공식 엔티티 가이드](https://developers.home-assistant.io/docs/core/entity/assist-satellite/)에 설명되어 있습니다. 이 업스트림 API는 음향 검증을 약속하지 않습니다. 여기서 따로 구분한 것은 설계 결정입니다.
