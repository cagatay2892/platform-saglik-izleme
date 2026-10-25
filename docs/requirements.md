# Sistem gereksinimleri

## Amaç

Sentetik platform telemetrisini API üzerinden almak, eşiklere göre olayları belirlemek, ölçümleri kalıcı olarak saklamak ve kullanıcıya görselleştirmek.

## Fonksiyonel gereksinimler

| Kimlik | Gereksinim |
|---|---|
| FR-01 | Kullanıcı normal çalışma veya üç arıza senaryosundan birini seçebilmelidir. |
| FR-02 | Simülatör sıcaklık, titreşim ve gerilim ölçümleri üretmelidir. |
| FR-03 | Ölçümler API'ye gönderilmeden önce alan türü ve fiziksel aralık bakımından doğrulanmalıdır. |
| FR-04 | API tanımlı eşikleri değerlendirip ölçüme uyarı durumu atamalıdır. |
| FR-05 | Her simülasyon ve ölçüm kaydı SQLite veritabanında saklanmalıdır. |
| FR-06 | Kullanıcı geçmiş simülasyonları seçip ölçümlerini ve uyarılarını görebilmelidir. |
| FR-07 | Kullanıcı seçili simülasyonun ölçümlerini CSV olarak indirebilmelidir. |
| FR-08 | API sağlık durumu ve senaryo listesi için uç sağlamalıdır. |

## Kalite gereksinimleri

| Kimlik | Gereksinim |
|---|---|
| QR-01 | Aynı senaryo, ölçüm sayısı ve tohum aynı ölçüm değerlerini üretmelidir. |
| QR-02 | Ölçüm verisi ile eşik değerlendirmesi kullanıcı arayüzünden ayrılmalıdır. |
| QR-03 | Veritabanı dosyası ve yerel çalışma ortamı GitHub'a gönderilmemelidir. |
| QR-04 | Kurulum yönergeleri API ve paneli ayrı terminalde başlatmayı açıklamalıdır. |
| QR-05 | Uygulama sentetik verinin ve eşik kurallarının sınırlarını açıklamalıdır. |
