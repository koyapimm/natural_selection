# Doğal Seleksiyon Simülasyonu

Bu proje, hız, algı menzili (sense) ve boyut (size) gibi özelliklerin evrimsel süreçte doğal seleksiyonla nasıl değiştiğini görselleştiren bir Pygame simülasyonudur.

## Canlı Jenerasyon Grafiği

- Simülasyon sırasında her gün jenerasyon bazlı popülasyon değişimi canlı olarak matplotlib penceresinde gösterilir.
- Her jenerasyon farklı renkte çizilir ve grafik otomatik güncellenir.
- Simülasyon sonunda tüm istatistikler ve jenerasyon grafiği `results.png` olarak kaydedilir.

## v0.4 – Jenerasyon Renkleri ve Gelişmiş Genetik Takip

- Her Blob nesnesi artık jenerasyonuna göre otomatik olarak farklı bir renkte çizilir (viridis renk skalası, matplotlib).
- Her gün sonunda jenerasyon başına hayatta kalan birey sayısı `genealogy.json` dosyasına kaydedilir (format: `{ "Gün 0": { "jenerasyon_0": 50 }, ... }`).
- Her 10 günde bir, jenerasyonlara göre popülasyon değişimini gösteren grafik otomatik olarak ekrana gelir ve PNG olarak kaydedilir (`results_10.png`, `results_20.png` ...).
- Tüm kodlar PEP8 uyumlu ve yorum satırlarıyla açıklanmıştır.

## v0.3 – Genetik Miras ve Grafiksel Çıktılar

- Genetik miras sistemi: Üreme sırasında yavruların genetik özellikleri %70 olasılıkla aynen aktarılır, %30 olasılıkla mutasyon uygulanır.
- Enerji maliyeti formülü kodda açıklama olarak belirtildi.
- Simülasyon sonunda popülasyon, ortalama hız, menzil ve boyutun günlük değişimini gösteren 4'lü grafik otomatik olarak çizilir.

## Dosya Yapısı

- `main.py`: Ana Pygame döngüsü ve simülasyon akışı
- `settings.py`: Sabitler ve simülasyon parametreleri
- `utils.py`: Yardımcı fonksiyonlar (mesafe, clamp)
- `food.py`: Food sınıfı
- `blob.py`: Blob sınıfı (canlılar)
- `simulation.py`: Simülasyonun ana fonksiyonları (üreme, yeme, istatistik, genetik kayıt)
- `graph.py`: Simülasyon verilerini toplayan ve sonuçları çizen modül
- `requirements.txt`: Bağımlılıklar
- `README.md`: Bu dosya

## Çalıştırma

1. Gerekli paketleri yükleyin:

```
pip install -r requirements.txt
```

2. Simülasyonu başlatın:

```
python main.py
```

## Kurallar ve Özellikler

- Her blob'un hızı, algı menzili ve boyutu vardır.
- Enerji maliyeti: `(size³) * (speed²)`
- Büyük bloblar küçük blobları yiyebilir.
- Renk: Hız arttıkça kırmızıdan beyaza geçer.
- Boyut: Çizimde yarıçap ile orantılıdır.
- Evrim: Üreme sırasında tüm özellikler mutasyonla aktarılır.
- Genetik takip: Jenerasyonlara göre popülasyon değişimi ve soyağacı kaydı tutulur.

## Geliştirme

Kod modülerdir ve kolayca yeni özellikler eklenebilir. Canlı istatistik grafikleri için `graph.py` eklenebilir. 