# Mimari notları

## Veri akışı

1. Kullanıcı arayüzden senaryo, ölçüm sayısı ve rastgelelik tohumunu seçer.
2. telemetry.py her sensör için sentetik ölçümler üretir.
3. Her ölçüm sıcaklık, titreşim ve gerilim eşikleriyle karşılaştırılır.
4. app.py grafik ve olay tablosunu oluşturur; aynı kayıtları CSV olarak indirmeye açar.

## Modüller

- app.py: Streamlit arayüzü, grafikler, uyarı tablosu ve CSV indirme.
- telemetry.py: tekrarlanabilir telemetri simülasyonu ve eşik tabanlı olay işaretleme.
- requirements.txt: uygulama bağımlılıkları.

## Tasarım sınırları

Bu sürümde veri kaynağı tamamen simülasyondur. Kalıcı veritabanı, gerçek sensör bağlantısı, kimlik doğrulama ve uzaktan iletişim yoktur. Bu sınır, portföy demosunun güvenli ve her geliştiricide kolayca çalıştırılabilir kalmasını sağlar.
