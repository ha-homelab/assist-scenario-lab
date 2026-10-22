# Evaluasi skenario suara yang direkam

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

## Instalasi dan batasan

Instal dari salinan repositori dengan `python3 -m pip install .` di lingkungan virtual. Python 3.11+ didukung. Tidak ada dependensi runtime selain Python. `assist-lab --help --lang en` menampilkan perintah; `ru`, `de`, dan `es` juga berfungsi. Titik masuk modulnya adalah `python3 -m assist_scenario_lab`.

Pemuatan berkas memerlukan flag sistem operasi `O_NOFOLLOW` dan `O_NONBLOCK`, yang tersedia di Linux dan macOS. Jika salah satunya tidak ada, CLI mengembalikan kode keluar 2 dengan `unsupported_platform` sebelum membuka masukan. API evaluasi dan impor Python dalam memori tidak memerlukan flag tersebut.

Ini adalah evaluator offline, bukan firmware satelit, detektor akustik, pengumpul langsung, integrasi HA, atau benchmark lengkap. Jalankan pengujian penerimaan produk yang sebenarnya dengan alat firmware yang sesuai. Berikan bukti hasilnya yang berukuran terbatas kepada alat ini hanya setelah memeriksa privasinya.

## Masukan kanonis

Mulai dari `examples/synthetic-pass.json`. Akar memerlukan `schema: assist-scenario-lab/v1`, boolean `synthetic`, objek `requirements`, dan 1–500 `sessions`. Kolom yang tidak dikenal ditolak. Sesi memiliki `id` unik serta `platform`, `scenario`, `clock`, `events`, dan `checks`. ID terdiri dari 1–64 huruf ASCII, angka, garis bawah, atau tanda hubung; dimulai dengan huruf atau angka. Gunakan nama samaran, bukan nama ruangan, alamat, atau pengenal perangkat.

`clock` bernilai `relative_monotonic` atau `utc_derived`. Peristiwa berisi `stage`, `at_ms`, `origin`. Waktu harus berhingga, tidak negatif, paling lama 12 jam, dan terurut tidak menurun. Peristiwa pertama adalah `request` pada nol. Setiap tahap muncul sekali. Tahap yang didukung: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Pipeline berbeda dapat melakukan streaming; sengaja tidak ada urutan tetap antara TTS dan pemutaran selain urutan kronologis stempel waktunya.

Asalnya adalah `pipeline`, `satellite`, `operator`, dan `acoustic`. Hanya `operator` atau `acoustic` yang boleh menjadi asal `audible_start`. Setiap sesi harus menyediakan ketiga pemeriksaan: `intent_correct`, `action_observed`, `audible`. Masing-masing memiliki `result` (`pass`, `fail`, `unknown`) dan `method`. Hasil tidak diketahui memerlukan `none`. Metode sah lainnya adalah `operator`/`intent_assertion` untuk maksud, `operator`/`ha_state` untuk tindakan, dan `operator`/`acoustic` untuk keterdengaran. Stempel waktu suara terdengar memerlukan pemeriksaan keterdengaran yang lulus. Alat memeriksa konsistensi, bukan kebenaran.

Persyaratan dapat mengaktifkan salah satu dari tiga pemeriksaan dan secara opsional `max_audible_ms`. Pemeriksaan yang dihilangkan atau bernilai false tidak diwajibkan: kebijakan khusus API dapat lulus tanpa bukti fisik dan harus diberi label demikian. Contoh bawaan mewajibkan semua pemeriksaan. Kesalahan pipeline selalu menyebabkan gagal. Ketiadaan `protocol_end` berarti tidak lengkap. Kegagalan persyaratan wajib mengalahkan pengamatan yang tidak diketahui. Latensi di atas ambang gagal; latensi wajib yang tidak ada berarti tidak lengkap.

## Mengimpor eksekusi HA

Adaptor menerima satu **array objek peristiwa**, bukan log WebSocket lengkap atau ZIP diagnostik. Ekstrak badan setiap peristiwa secara lokal. Objek memiliki tepat `type`, `timestamp`, `data`; data boleh berupa objek atau null. Stempel waktu harus berupa ISO 8601 dengan zona waktu. Mulai dengan `run-start`, pertahankan urutan kronologis, dan jangan mencampur eksekusi. Tahap terpetakan yang berulang ditolak.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

Perintah kedua sengaja mengembalikan 3. `run-end` dipetakan menjadi `protocol_end`, bukan keberhasilan fisik. `tts-end` menjadi `tts_ready`, bukan suara terdengar. Semua `data` dibuang, termasuk transkrip, teks masukan, kesalahan, URL/token TTS, dan metadata pipeline. Peristiwa awal, kemajuan, dan VAD dikenali tetapi tidak disimpan. Waktu hasil konversi memakai `utc_derived`: pengurangan waktu jam bukan pengukuran latensi monoton dan dapat terpengaruh koreksi jam. Ketiga pemeriksaan fisik/semantik tetap tidak diketahui.

## Laporan dan perbandingan

`--format text|json|html|junit` memilih laporan. Pengalihan shell menulis hasil ke jalur lokal pilihan. CLI tidak pernah menimpa masukan dengan sendirinya. Kode keluar: 0, persyaratan tercatat lulus; 1, gagal; 2, masukan/argumen tidak sah; 3, tidak lengkap. JUnit menampilkan sesi tidak lengkap sebagai dilewati; CI tetap harus menghormati kode 3.

Kelompok JSON memakai platform + skenario + jam + metode pengukuran waktu keterdengaran. Jangan memperlakukan jam berbeda atau pengamatan manusia dan akustik sebagai pengukuran yang dapat saling menggantikan. p50/p95 memakai metode peringkat terdekat. p95 bernilai null di bawah 20 sampel; 20 adalah ambang pelaporan, bukan bukti keyakinan statistik. Sesi gagal dengan audio yang teramati tetap masuk populasi sampel latensi, dan jumlah kegagalannya tetap terlihat. Jangan memilih hanya percobaan yang lulus. Audio mentah dan transkrip tidak diekspor. ID masih dapat mengungkap informasi, jadi periksalah.

HTML mencantumkan semua sesi dan menggambar 50 pengamatan terdengar pertama dengan skala bersama. Baca platform dan metode setiap baris; ringkasan bukan peringkat statistik. `evidence_verified: false` selalu ada. `synthetic: false` berarti penulis tidak menandai eksekusi sebagai sintetis, bukan berarti perangkat keras telah divalidasi secara independen.

## Mengumpulkan bukti yang bermakna

Tentukan maksud yang diharapkan dan target sebelum percobaan. Definisikan peristiwa awal secara konsisten: permintaan pipeline belum tentu awal ucapan. Simpan catatan percobaan terpisah yang memuat versi perangkat lunak, bahasa, kondisi jaringan, posisi mikrofon dan pengeras suara, metode pengamatan, serta jumlah percobaan. Gunakan pengukuran akustik yang sesuai untuk waktu suara terdengar yang presisi; jangan menggantinya dengan potongan jaringan pertama. Catat kegagalan, timeout, dan bukti yang hilang. Paket ini tidak melakukan sinkronisasi akustik atau pengelolaan persetujuan.

## Pemecahan masalah

- `object_fields`: bandingkan kunci dengan fixture kanonis; dump diagnostik lengkap tidak diterima.
- `ha_timestamp` / `time_order`: ekspor satu eksekusi, sertakan zona waktu, dan periksa koreksi jam. Jangan mengubah urutan peristiwa untuk merekayasa latensi.
- `stage`: tahap tidak dikenal atau duplikat; periksa apakah dua eksekusi digabung.
- `audible_origin` / `conflicting_audible`: metadata pemutaran tidak menggantikan pendengaran suara.
- Kode 3 setelah API berhasil: wajar sampai pengamatan wajib dicatat.
- `unsupported_platform`: OS tidak menyediakan `O_NOFOLLOW` atau `O_NONBLOCK`; gunakan lingkungan dengan keduanya (Linux atau macOS). Masukan ditolak sebelum dibuka, bukan melonggarkan pemeriksaan symlink atau FIFO.
- `file_size_type`: hanya berkas JSON UTF-8 biasa, maksimum 2 MiB. Direktori, FIFO, dan symlink pada komponen terakhir ditolak. Symlink di direktori induk bukan batas sandbox.
- `number`: stempel waktu tidak boleh negatif, tidak berhingga, boolean, atau lebih dari 12 jam.

Kesalahan menampilkan ringkasan terjemahan dan kode tetap, bukan isi sumber atau jalur lokal. Contoh publik sepenuhnya sintetis. Simpan ekspor di luar salinan repositori ini, sebaiknya dalam direktori sementara privat.

## Arsitektur, terjemahan, dan sumber

![Alur offline](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` menangani validasi, impor, dan evaluasi murni; `cli.py` merender format; `locales/*.json` berisi empat katalog. Pengujian mewajibkan kesetaraan kunci katalog. Kunci mesin dan kode diagnostik tidak diterjemahkan. Panduan lengkap mencakup 24 bahasa dokumentasi ha-homelab; CLI dan README tetap dalam bahasa Inggris, Rusia, Jerman, dan Spanyol. Sumbangkan terjemahan referensi tambahan dengan pemeriksaan kesetaraan dan contoh yang ditinjau.

Pemetaan protokol diperiksa terhadap [dokumentasi Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) dan [model peristiwa HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). Siklus hidup satelit dijelaskan dalam [panduan entitas resmi](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). API upstream tersebut tidak menjanjikan verifikasi akustik; memisahkannya di sini adalah keputusan desain.
