# Doğal Seleksiyon Simülasyonu

Bu proje, hız, algı menzili (sense) ve boyut (size) gibi özelliklerin evrimsel süreçte doğal seleksiyonla nasıl değiştiğini görselleştiren bir Pygame simülasyonudur.

## Dosya Yapısı

- `main.py`: Ana Pygame döngüsü ve simülasyon akışı
- `settings.py`: Sabitler ve simülasyon parametreleri
- `utils.py`: Yardımcı fonksiyonlar (mesafe, clamp)
- `food.py`: Food sınıfı
- `blob.py`: Blob sınıfı (canlılar)
- `simulation.py`: Simülasyonun ana fonksiyonları (üreme, yeme, istatistik)
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

## Geliştirme

Kod modülerdir ve kolayca yeni özellikler eklenebilir. Canlı istatistik grafikleri için `graphs.py` eklenebilir. 