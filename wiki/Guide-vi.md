# Đánh giá kịch bản giọng nói đã ghi lại

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

## Cài đặt và giới hạn

Cài từ bản sao kho mã bằng `python3 -m pip install .` trong môi trường ảo. Hỗ trợ Python 3.11+. Không có phụ thuộc lúc chạy ngoài Python. `assist-lab --help --lang en` liệt kê lệnh; `ru`, `de` và `es` cũng dùng được. Điểm vào qua mô-đun là `python3 -m assist_scenario_lab`.

Nạp tệp đòi hỏi cờ hệ điều hành `O_NOFOLLOW` và `O_NONBLOCK`, có trên Linux và macOS. Nếu thiếu một trong hai, CLI trả mã thoát 2 với `unsupported_platform` trước khi mở đầu vào. Các API Python đánh giá và nhập dữ liệu trong bộ nhớ không cần các cờ này.

Đây là bộ đánh giá ngoại tuyến, không phải firmware thiết bị vệ tinh, bộ phát hiện âm thanh, bộ thu thập trực tiếp, tích hợp HA hay bộ benchmark đầy đủ. Hãy thực hiện kiểm thử chấp nhận sản phẩm thật bằng công cụ firmware phù hợp. Chỉ cung cấp bằng chứng kết quả có giới hạn cho công cụ này sau khi rà soát quyền riêng tư.

## Đầu vào chuẩn

Bắt đầu từ `examples/synthetic-pass.json`. Gốc yêu cầu `schema: assist-scenario-lab/v1`, giá trị boolean `synthetic`, đối tượng `requirements` và 1–500 `sessions`. Trường không biết bị từ chối. Một phiên có `id` duy nhất cùng `platform`, `scenario`, `clock`, `events` và `checks`. ID gồm 1–64 chữ ASCII, chữ số, dấu gạch dưới hoặc gạch nối; bắt đầu bằng chữ hoặc số. Dùng bí danh, không dùng tên phòng, địa chỉ hay định danh thiết bị.

`clock` là `relative_monotonic` hoặc `utc_derived`. Sự kiện chứa `stage`, `at_ms`, `origin`. Thời gian phải hữu hạn, không âm, tối đa 12 giờ và theo thứ tự không giảm. Sự kiện đầu là `request` tại mốc không. Mỗi giai đoạn xuất hiện một lần. Các giai đoạn hỗ trợ: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Các pipeline khác nhau có thể truyền luồng; ngoài trình tự dấu thời gian, công cụ cố ý không cố định thứ tự giữa TTS và phát âm thanh.

Nguồn là `pipeline`, `satellite`, `operator` và `acoustic`. Chỉ `operator` hoặc `acoustic` được tạo `audible_start`. Mỗi phiên phải cung cấp đủ ba kiểm tra: `intent_correct`, `action_observed`, `audible`. Mỗi kiểm tra có `result` (`pass`, `fail`, `unknown`) và `method`. Kết quả chưa biết yêu cầu `none`. Các phương pháp hợp lệ khác là `operator`/`intent_assertion` cho ý định, `operator`/`ha_state` cho hành động và `operator`/`acoustic` cho khả năng nghe thấy. Dấu thời gian nghe thấy đòi hỏi kiểm tra khả năng nghe đạt. Công cụ kiểm tra tính nhất quán, không xác nhận sự thật.

Yêu cầu có thể bật bất kỳ kiểm tra nào trong ba loại và thêm `max_audible_ms` tùy chọn. Kiểm tra bị bỏ qua hoặc đặt false không bắt buộc: chính sách chỉ xét API có thể đạt mà không có bằng chứng vật lý và phải được ghi nhãn như vậy. Ví dụ đi kèm yêu cầu mọi kiểm tra. Lỗi pipeline luôn gây thất bại. Thiếu `protocol_end` là chưa đầy đủ. Một yêu cầu thất bại được ưu tiên hơn quan sát chưa biết. Độ trễ vượt ngưỡng gây thất bại; thiếu độ trễ bắt buộc là chưa đầy đủ.

## Nhập một lần chạy HA

Bộ chuyển đổi nhận một **mảng đối tượng sự kiện**, không nhận toàn bộ log WebSocket hay ZIP chẩn đoán. Trích xuất nội dung từng sự kiện tại máy. Đối tượng có đúng `type`, `timestamp`, `data`; dữ liệu có thể là đối tượng hoặc null. Dấu thời gian phải theo ISO 8601 có múi giờ. Bắt đầu với `run-start`, giữ thứ tự thời gian và không trộn lần chạy. Các giai đoạn đã ánh xạ bị lặp sẽ bị từ chối.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

Lệnh thứ hai cố ý trả 3. `run-end` ánh xạ thành `protocol_end`, không phải thành công vật lý. `tts-end` ánh xạ thành `tts_ready`, không phải âm thanh nghe thấy. Mọi `data` bị loại, gồm bản chép lời, văn bản đầu vào, lỗi, URL/token TTS và siêu dữ liệu pipeline. Sự kiện bắt đầu, tiến độ và VAD được nhận diện nhưng không giữ lại. Thời gian chuyển đổi dùng `utc_derived`: trừ giờ đồng hồ không phải phép đo độ trễ đơn điệu và có thể bị ảnh hưởng khi chỉnh đồng hồ. Cả ba kiểm tra vật lý/ngữ nghĩa vẫn chưa biết.

## Báo cáo và so sánh

`--format text|json|html|junit` chọn báo cáo. Chuyển hướng shell ghi kết quả vào đường dẫn cục bộ đã chọn. CLI không bao giờ tự ghi đè đầu vào. Mã thoát: 0, yêu cầu ghi nhận đã đạt; 1, thất bại; 2, đầu vào/đối số không hợp lệ; 3, chưa đầy đủ. JUnit biểu diễn phiên chưa đầy đủ thành bỏ qua; CI vẫn phải tôn trọng mã 3.

Nhóm JSON dùng nền tảng + kịch bản + đồng hồ + phương pháp đo thời điểm nghe thấy. Không bao giờ xem các đồng hồ khác nhau hoặc quan sát của người và đo âm học là phép đo thay thế được cho nhau. p50/p95 dùng phương pháp thứ hạng gần nhất. p95 là null khi dưới 20 mẫu; 20 là ngưỡng báo cáo, không phải bằng chứng về độ tin cậy thống kê. Phiên thất bại có âm thanh được quan sát vẫn nằm trong tập mẫu độ trễ và số thất bại vẫn hiện rõ. Không chọn riêng những lần thử đạt. Không xuất âm thanh thô hay bản chép lời. ID vẫn có thể tiết lộ thông tin, nên hãy rà soát.

HTML liệt kê mọi phiên và vẽ 50 quan sát nghe thấy đầu tiên trên cùng thang đo. Đọc nền tảng/phương pháp của từng hàng; tổng quan không phải bảng xếp hạng thống kê. `evidence_verified: false` luôn có mặt. `synthetic: false` nghĩa là tác giả không đánh dấu lần chạy là tổng hợp, không nghĩa phần cứng đã được kiểm chứng độc lập.

## Thu thập bằng chứng có ý nghĩa

Xác định ý định dự kiến và mục tiêu trước mỗi lần thử. Chọn sự kiện bắt đầu nhất quán: yêu cầu pipeline không nhất thiết là lúc bắt đầu câu nói. Giữ nhật ký thử nghiệm riêng với phiên bản phần mềm, ngôn ngữ, điều kiện mạng, vị trí micro và loa, phương pháp quan sát và số lần thử. Dùng phép đo âm học phù hợp để xác định chính xác lúc nghe thấy; đừng thay bằng khối mạng đầu tiên. Ghi lại thất bại, hết thời gian và bằng chứng thiếu. Gói này không đồng bộ âm học hay quản lý sự đồng ý.

## Khắc phục sự cố

- `object_fields`: so sánh khóa với fixture chuẩn; không chấp nhận toàn bộ bản kết xuất chẩn đoán.
- `ha_timestamp` / `time_order`: xuất một lần chạy, thêm múi giờ và xem các lần chỉnh đồng hồ. Không sắp xếp lại sự kiện để tạo ra độ trễ mong muốn.
- `stage`: giai đoạn không biết hoặc trùng; kiểm tra có ghép hai lần chạy không.
- `audible_origin` / `conflicting_audible`: siêu dữ liệu phát âm thanh không thay thế việc nghe thấy.
- Mã 3 sau API thành công: đúng như dự kiến cho đến khi ghi nhận các quan sát bắt buộc.
- `unsupported_platform`: hệ điều hành thiếu `O_NOFOLLOW` hoặc `O_NONBLOCK`; dùng môi trường có cả hai (Linux hoặc macOS). Đầu vào bị từ chối trước khi mở thay vì nới lỏng kiểm tra liên kết tượng trưng hoặc FIFO.
- `file_size_type`: chỉ tệp JSON UTF-8 thông thường, tối đa 2 MiB. Thư mục, FIFO và liên kết tượng trưng ở thành phần cuối bị từ chối. Liên kết trong thư mục cha không phải ranh giới sandbox.
- `number`: dấu thời gian không được âm, không hữu hạn, có kiểu boolean hoặc quá 12 giờ.

Lỗi in bản tóm tắt đã dịch và mã ổn định, không in nội dung nguồn hay đường dẫn cục bộ. Ví dụ công khai hoàn toàn tổng hợp. Giữ dữ liệu xuất ngoài bản sao kho mã này, ưu tiên thư mục tạm riêng tư.

## Kiến trúc, bản dịch và nguồn

![Luồng ngoại tuyến](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` xử lý xác thực, nhập và đánh giá thuần túy; `cli.py` dựng các định dạng; `locales/*.json` chứa bốn danh mục. Kiểm thử yêu cầu khóa danh mục tương đương. Khóa máy và mã chẩn đoán không được dịch. Hướng dẫn đầy đủ bao phủ 24 ngôn ngữ tài liệu ha-homelab; CLI và README vẫn là tiếng Anh, Nga, Đức và Tây Ban Nha. Hãy đóng góp thêm bản dịch tham chiếu kèm kiểm tra tương đương và ví dụ đã rà soát.

Ánh xạ giao thức được kiểm tra theo [tài liệu Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) và [mô hình sự kiện HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). Vòng đời thiết bị vệ tinh được mô tả trong [hướng dẫn thực thể chính thức](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Các API thượng nguồn này không hứa xác minh âm học; tách riêng ở đây là quyết định thiết kế.
