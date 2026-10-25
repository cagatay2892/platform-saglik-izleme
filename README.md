# Platform Sağlık İzleme Simülatörü
Sentetik veri notu: Bu projedeki tüm ölçümler yazılım tarafından üretilir; gerçek sensör, platform veya operasyon verisi kullanılmaz. Eşikler demo amacıyla seçilmiştir. Proje eşik tabanlı uyarı gösterir; arıza tahmini ya da operasyonel kullanım iddiası yoktur.
Sentetik telemetriyle çalışan, eşik tabanlı bir sağlık izleme demosu. Python simülatörü ölçüm üretir, FastAPI bu ölçümleri doğrular, SQLite geçmişi saklar ve Streamlit paneli kayıtlı simülasyonları görselleştirir.


## Özellikler

- Normal çalışma, aşırı ısınma, yüksek titreşim ve gerilim düşümü senaryoları
- FastAPI ile ölçüm kaydetme ve geçmiş veriyi sunma
- SQLite'ta kalıcı simülasyon ve ölçüm geçmişi
- API üzerinden alınan, doğrulanan sensör ölçümleri
- Eşik çizgileriyle etkileşimli grafikler ve olay tablosu
- Seçili simülasyonu CSV olarak indirme
- FastAPI tarafından üretilen etkileşimli API belgeleri

## Gerekli araçlar

- Python 3.10 veya üzeri

## Windows'ta çalıştırma

Proje klasöründe PowerShell aç.

### İlk kurulum

~~~powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

### 1. terminal: API sunucusu

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
~~~

API hazır olduğunda belgeleri http://127.0.0.1:8000/docs adresinde açabilirsin.

### 2. terminal: gösterge paneli

Yeni bir PowerShell penceresi açıp aynı proje klasörüne geç ve çalıştır:

~~~powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
~~~

Streamlit adresini açınca bir senaryo seçip “Senaryoyu üret ve kaydet” düğmesine bas. API servisini ve paneli aynı anda açık tut.

## Veri akışı

~~~mermaid
flowchart LR
    A[Sentetik veri üreticisi] -->|JSON ölçümler| B[FastAPI]
    B -->|doğrulama ve eşik kontrolü| C[SQLite]
    C -->|geçmiş ölçüm ve olaylar| D[Streamlit paneli]
~~~

## API uçları

| Yöntem | Uç | Açıklama |
|---|---|---|
| GET | /health | API ve veritabanı durumunu bildirir |
| GET | /scenarios | Kullanılabilir simülasyon senaryolarını listeler |
| POST | /simulations | Bir simülasyonu ve ölçümlerini kaydeder |
| GET | /simulations | Son simülasyonları listeler |
| GET | /simulations/{id}/measurements | Seçili simülasyonun ölçümlerini getirir |
| GET | /simulations/{id}/alerts | Seçili simülasyonun uyarılarını getirir |

## Eşikler

| Ölçüm | Uyarı koşulu |
|---|---:|
| Sıcaklık | 70 °C üzeri |
| Titreşim | 1,2 g üzeri |
| Gerilim | 21 V altı |

Değerler yalnızca demo davranışını göstermek amacıyla seçilmiştir; teknik gereksinim veya gerçek platform sınırı değildir.

## Veri saklama

Veriler proje klasöründe oluşan telemetry.db dosyasında tutulur. Bu dosya .gitignore ile GitHub'a gönderilmez. Geçmişi sıfırlamak için API sunucusunu durdurup telemetry.db dosyasını silebilirsin.

## Kapsam ve sınırlar

Bu çalışma; API tasarımı, veri doğrulama, yerel veritabanı kullanımı ve görselleştirme çalışmalarını bir araya getirir. Gerçek sensör bağlantısı, kullanıcı kimlik doğrulaması, ağ üzerinden uzaktan erişim, makine öğrenmesi veya güvenlik sertifikasyonu içermez.
