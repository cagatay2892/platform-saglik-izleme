# Mimari notları

## Veri akışı

1. Streamlit panelinde senaryo, ölçüm sayısı ve rastgelelik tohumu seçilir.
2. telemetry.py seçilen senaryo için tekrarlanabilir sentetik ölçümler üretir.
3. Panel ölçüm listesini JSON olarak FastAPI'deki POST /simulations ucuna gönderir.
4. API, Pydantic modeliyle veri türlerini ve tanımlı aralıkları doğrular.
5. API ortak eşik kurallarını uygular ve simülasyon ile ölçümleri SQLite'a kaydeder.
6. Panel simülasyon geçmişini API'den okur; grafikleri, uyarıları ve CSV indirmesini sunar.

## Modüller

- app.py: Streamlit arayüzü ve API istemcisi.
- api.py: FastAPI uçları, istek doğrulama ve eşik değerlendirmesi.
- database.py: SQLite şeması ve kalıcılık işlemleri.
- telemetry.py: senaryo tanımları, eşikler ve sentetik ölçüm üretimi.
- requirements.txt: uygulama bağımlılıkları.

## Veritabanı

- simulation_runs: senaryo adı, oluşturulma zamanı ve çalışma kimliği.
- measurements: ölçüm zaman damgası, sıcaklık, titreşim, gerilim, durum ve uyarılar.

Veritabanı proje klasöründeki telemetry.db dosyasında tutulur. Dosya .gitignore tarafından dışarıda bırakılır.

## API uçları

- GET /health
- GET /scenarios
- POST /simulations
- GET /simulations
- GET /simulations/{id}/measurements
- GET /simulations/{id}/alerts

FastAPI belgeleri /docs yolunda sunulur.

## Tasarım sınırları

Bu sürümde veri kaynağı tamamen simülasyondur. Gerçek sensör bağlantısı, kullanıcı kimlik doğrulaması ve uzak erişim yoktur. SQLite tek dosyalı yerel veritabanı olarak geliştirme demosu için kullanılır; bu mimari operasyonel platform entegrasyonu veya sertifikasyon iddiası taşımaz.
