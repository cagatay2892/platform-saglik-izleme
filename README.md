# Platform Sağlık İzleme Simülatörü

Sentetik telemetriyle çalışan, eşik tabanlı bir sağlık izleme demosu. Sıcaklık, titreşim ve gerilim ölçümlerini üretir; seçilen senaryoya göre arıza belirtilerini simüle eder ve ölçümleri etkileşimli bir panelde gösterir.

> Bu proje bir portföy simülasyonudur. Gerçek platform verisi veya donanım bağlantısı içermez. Eşik tabanlı uyarılar verir; arıza tahmini ya da operasyonel kullanım iddiası yoktur.

## Özellikler

- Normal çalışma, aşırı ısınma, yüksek titreşim ve gerilim düşümü senaryoları
- Tekrarlanabilir sentetik veri üretimi
- Ayarlanabilir ölçüm sayısı ve rastgelelik tohumu
- Eşik çizgileriyle etkileşimli grafikler
- Uyarı olaylarının tablo görünümü
- Telemetriyi CSV olarak indirme

## Başlangıç

Python 3.10 veya üzeri gerekir.

Windows PowerShell:

~~~powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
streamlit run app.py
~~~

Komut çalışınca Streamlit yerel adresini tarayıcıda aç. Uygulamada senaryo ve ölçüm sayısını değiştirerek paneli inceleyebilirsin.

## Mimari

~~~mermaid
flowchart LR
    A[Senaryo seçimi] --> B[Sentetik telemetri üreticisi]
    B --> C[Eşik tabanlı olay işaretleme]
    C --> D[Streamlit paneli]
    C --> E[CSV dışa aktarımı]
~~~

## Eşikler

| Ölçüm | Uyarı koşulu |
|---|---:|
| Sıcaklık | 70 °C üzeri |
| Titreşim | 1,2 g üzeri |
| Gerilim | 21 V altı |

Değerler yalnızca demo davranışını göstermek amacıyla seçilmiştir; teknik gereksinim veya gerçek platform sınırı değildir.

## Kapsam

Proje; yazılım geliştirme, telemetri görselleştirme, basit veri analizi ve sistem dokümantasyonu çalışmalarını bir araya getirir. Gerçek sistem entegrasyonu, donanım sürücüsü, makine öğrenmesi veya güvenlik sertifikasyonu içermez.

## Portföyde sunum

GitHub deposuna uygulama ekran görüntüsü veya kısa ekran kaydı ekle. README'de senaryoları, kullanılan teknolojileri ve kapsam sınırlarını koru. Projeyi gerçekten tamamladıktan sonra CV'de örneğin şöyle özetleyebilirsin:

> Python ve Streamlit ile sentetik platform telemetrisini görselleştiren bir sağlık izleme demosu geliştirdim; eşik tabanlı uyarılar, olay kayıtları ve CSV dışa aktarımı ekledim.

## Dosyalar

- app.py — Streamlit arayüzü
- telemetry.py — sentetik ölçüm üretimi ve eşik kuralları
- docs/ — proje gereksinimleri ve mimari notları

