# Kaydedilmiş sesli senaryoların değerlendirilmesi

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

## Kurulum ve sınırlar

Bir çalışma kopyasından, sanal ortamda `python3 -m pip install .` ile kurun. Python 3.11+ desteklenir. Python dışında çalışma zamanı bağımlılığı yoktur. `assist-lab --help --lang en` komutları listeler; `ru`, `de` ve `es` de çalışır. Modül giriş noktası `python3 -m assist_scenario_lab` komutudur.

Dosya yükleme, Linux ve macOS'ta bulunan `O_NOFOLLOW` ve `O_NONBLOCK` işletim sistemi bayraklarını gerektirir. Bunlardan biri yoksa CLI girdiyi açmadan önce `unsupported_platform` ile çıkış kodu 2 döndürür. Bellekteki Python değerlendirme ve içe aktarma API'leri bu bayrakları gerektirmez.

Bu bir çevrimdışı değerlendiricidir; uydu aygıt yazılımı, akustik algılayıcı, canlı veri toplayıcı, HA entegrasyonu veya eksiksiz performans testi değildir. Gerçek ürün kullanıcı kabul testlerini uygun aygıt yazılımı araçlarıyla yapın. Elde edilen sınırlı kapsamlı kanıtları bu araca ancak gizliliği inceledikten sonra verin.

## Standart girdi

`examples/synthetic-pass.json` ile başlayın. Kök; `schema: assist-scenario-lab/v1`, Boolean `synthetic`, bir `requirements` nesnesi ve 1–500 `sessions` gerektirir. Bilinmeyen alanlar reddedilir. Oturumun benzersiz bir `id` değeri ile `platform`, `scenario`, `clock`, `events` ve `checks` alanları vardır. Kimlikler 1–64 ASCII harfi, rakam, alt çizgi veya tire içerir; harf veya rakamla başlar. Oda adları, adresler veya cihaz kimlikleri yerine takma ad kullanın.

`clock`, `relative_monotonic` veya `utc_derived` olur. Olaylar `stage`, `at_ms`, `origin` içerir. Zamanlar sonlu, negatif olmayan, en fazla 12 saatlik ve azalmayan sıradadır. İlk olay sıfır anında `request` olur. Her aşama bir kez oluşur. Desteklenen aşamalar: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Farklı işlem hatları akış kullanabilir; bu nedenle kronolojik zaman damgalarının ötesinde TTS ile oynatma arasında bilerek sabit sıra yoktur.

Kaynaklar `pipeline`, `satellite`, `operator` ve `acoustic` değerleridir. Yalnızca `operator` veya `acoustic`, `audible_start` kaynağı olabilir. Her oturum üç kontrolün tamamını sağlamalıdır: `intent_correct`, `action_observed`, `audible`. Her birinde `result` (`pass`, `fail`, `unknown`) ve `method` vardır. Bilinmeyen sonuç `none` gerektirir. Diğer geçerli yöntemler niyet için `operator`/`intent_assertion`, eylem için `operator`/`ha_state`, duyulabilirlik için `operator`/`acoustic` değerleridir. Duyulabilir zaman damgası başarılı duyulabilirlik kontrolü gerektirir. Araç gerçeği değil, tutarlılığı doğrular.

Gereksinimler üç kontrolden herhangi birini ve isteğe bağlı `max_audible_ms` alanını etkinleştirebilir. Atlanmış veya false kontroller zorunlu değildir: yalnızca API'yi kapsayan politika fiziksel kanıt olmadan geçebilir ve böyle etiketlenmelidir. Birlikte gelen örnekler tüm kontrolleri gerektirir. İşlem hattı hatası her zaman başarısızlıktır. `protocol_end` eksikse sonuç tamamlanmamıştır. Zorunlu bir başarısızlık bilinmeyen gözlemlere üstün gelir. Eşiği aşan gecikme başarısızlıktır; zorunlu gecikmenin bulunmaması eksikliktir.

## HA çalıştırmasını içe aktarma

Bağdaştırıcı, tam WebSocket günlüğü veya tanı ZIP'i değil, bir **olay nesneleri dizisi** alır. Her olayın gövdesini yerel olarak çıkarın. Nesnelerde tam olarak `type`, `timestamp`, `data` bulunur; veri nesne veya null olabilir. Zaman damgaları saat dilimi içeren ISO 8601 olmalıdır. `run-start` ile başlayın, kronolojik sırayı koruyun ve çalıştırmaları karıştırmayın. Eşlenen aşamaların tekrarları reddedilir.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

İkinci komut bilerek 3 döndürür. `run-end`, fiziksel başarıya değil `protocol_end` değerine eşlenir. `tts-end`, duyulabilir sese değil `tts_ready` değerine eşlenir. Konuşma dökümleri, girdi metni, hatalar, TTS URL'leri/token'ları ve işlem hattı meta verileri dahil tüm `data` atılır. Başlangıç, ilerleme ve VAD olayları tanınır ama saklanmaz. Dönüştürülen zamanlar `utc_derived` kullanır: duvar saati çıkarımı monoton gecikme ölçümü değildir ve saat düzeltmelerinden etkilenebilir. Üç fiziksel/anlamsal kontrol de bilinmeyen olarak kalır.

## Raporlar ve karşılaştırma

`--format text|json|html|junit` raporu seçer. Kabuk yönlendirmesi sonucu seçilen yerel yola yazar. CLI kendi başına girdinin üzerine asla yazmaz. Çıkış kodları: 0, kaydedilen gereksinimler geçti; 1, başarısız; 2, geçersiz girdi/argüman; 3, eksik. JUnit eksik oturumları atlanmış olarak gösterir; CI yine de çıkış 3'ü dikkate almalıdır.

JSON grupları platform + senaryo + saat + duyulabilir zamanlama yöntemini kullanır. Farklı saatleri veya insan ve akustik gözlemleri asla birbirinin yerine geçen ölçümler olarak karşılaştırmayın. p50/p95 en yakın sıra yöntemini kullanır. 20 örneğin altında p95 null olur; 20, raporlama eşiğidir, istatistiksel güven kanıtı değildir. Ses gözlenmiş başarısız oturumlar gecikme örnekleminde kalır ve başarısızlık sayıları görünür olmaya devam eder. Yalnızca geçen denemeleri seçmeyin. Ham ses veya konuşma dökümü dışa aktarılmaz. Kimlikler yine de bilgi açığa çıkarabilir; onları inceleyin.

HTML tüm oturumları listeler ve ilk 50 duyulabilir gözlemi ortak ölçekle çizer. Her satırın platformunu ve yöntemini okuyun; genel görünüm istatistiksel sıralama değildir. `evidence_verified: false` her zaman bulunur. `synthetic: false`, yazarın çalıştırmayı sentetik olarak işaretlemediği anlamına gelir; donanımın bağımsız doğrulandığı anlamına gelmez.

## Anlamlı kanıt toplama

Denemeden önce beklenen niyeti ve hedefi tanımlayın. Başlangıç olayını tutarlı seçin: işlem hattı isteği söylenen ifadenin başlangıcı olmayabilir. Yazılım sürümleri, dil, ağ koşulları, mikrofon ve hoparlör yerleşimi, gözlem yöntemi ve deneme sayısını içeren ayrı bir deneme kaydı tutun. Kesin duyulabilir zamanlama için uygun akustik ölçüm kullanın; bunun yerine ilk ağ parçasını koymayın. Başarısızlıkları, zaman aşımlarını ve eksik kanıtları kaydedin. Paket akustik eşitleme veya rıza yönetimi gerçekleştirmez.

## Sorun giderme

- `object_fields`: anahtarları standart test verisiyle karşılaştırın; tam tanı dökümü kabul edilmez.
- `ha_timestamp` / `time_order`: tek çalıştırma dışa aktarın, saat dilimlerini ekleyin, saat düzeltmelerini inceleyin. Gecikme üretmek için olayları yeniden sıralamayın.
- `stage`: aşama bilinmiyor veya yinelenmiş; iki çalıştırmanın birleştirilip birleştirilmediğini kontrol edin.
- `audible_origin` / `conflicting_audible`: oynatma meta verisi sesi duymanın yerine geçemez.
- Başarılı API'den sonra çıkış 3: zorunlu gözlemler kaydedilene kadar beklenir.
- `unsupported_platform`: işletim sisteminde `O_NOFOLLOW` veya `O_NONBLOCK` eksik; ikisini sağlayan bir ortam kullanın (Linux veya macOS). Sembolik bağlantı veya FIFO kontrollerini gevşetmek yerine girdi açılmadan reddedilir.
- `file_size_type`: yalnızca normal UTF-8 JSON dosyaları, en fazla 2 MiB. Dizinler, FIFO'lar ve son yol bileşenindeki sembolik bağlantılar reddedilir. Üst dizin sembolik bağlantıları kum havuzu sınırı değildir.
- `number`: negatif, sonlu olmayan, Boolean veya 12 saati aşan zaman damgaları kabul edilmez.

Hatalar kaynak içeriği veya yerel yollar yerine çevrilmiş özet ve sabit kod yazdırır. Açık örnekler tamamen sentetiktir. Dışa aktarılan verileri bu çalışma kopyasının dışında, tercihen özel geçici dizinde tutun.

## Mimari, çeviriler ve kaynaklar

![Çevrimdışı akış](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` saf doğrulama, içe aktarma ve değerlendirmeyi yapar; `cli.py` biçimleri üretir; `locales/*.json` dört katalog içerir. Testler katalog anahtarlarının eşitliğini gerektirir. Makine anahtarları ve tanı kodları çevrilmez. Tam kılavuzlar ha-homelab'ın 24 belge dilini kapsar; CLI ve README İngilizce, Rusça, Almanca ve İspanyolca kalır. Eşlik testleri ve incelenmiş örneklerle ek referans çevirilerine katkıda bulunun.

Protokol eşlemesi [Home Assistant Assist belgeleri](https://developers.home-assistant.io/docs/voice/pipelines/) ve [HA 2026.10.0 olay modelleri](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py) ile doğrulanmıştır. Uydu yaşam döngüsü [resmî varlık kılavuzunda](https://developers.home-assistant.io/docs/core/entity/assist-satellite/) açıklanır. Bu upstream API'ler akustik doğrulama vaat etmez; burada ayrı tutulması bir tasarım kararıdır.
