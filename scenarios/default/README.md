# Varsayılan Senaryo

## Açıklama
Bu senaryo, Ecosim'in temel evrimsel simülasyon özelliklerini gösterir. Doğal seçilim, genetik mutasyon ve popülasyon dinamiklerini gözlemleyebilirsiniz.

## Özellikler
- **Doğal Seçilim**: Organizmalar yiyecek bulma ve hayatta kalma konusunda rekabet eder
- **Genetik Mutasyon**: Her üremede DNA'da rastgele değişiklikler oluşur
- **Popülasyon Dinamikleri**: Popülasyon büyüklüğü çevresel koşullara göre değişir
- **Çevresel Değişiklikler**: Yiyecek üretim oranı ve dünya boyutu zamanla değişir

## Parametreler
- **Başlangıç Organizmaları**: 100
- **Mutasyon Oranı**: %10
- **Yiyecek Üretim Oranı**: %5
- **Dünya Boyutu**: 2000x2000

## Olaylar
1. **Popülasyon Patlaması**: Popülasyon 200'ü geçtiğinde yiyecek üretimi artar
2. **Uygunluk Zirvesi**: Ortalama uygunluk 100'ü geçtiğinde agresif organizmalar eklenir
3. **Zaman Dönümü**: 60 saniye sonra dünya genişletilir

## Çalıştırma
```bash
python main.py --scenario default
```

## Beklenen Davranışlar
- Organizmalar yiyecek arayışında dolaşır
- Başarılı organizmalar çoğalır ve genlerini aktarır
- Popülasyon dalgalanmaları gözlenir
- Çevresel değişiklikler popülasyonu etkiler

## İstatistikler
- Nesil sayısı
- Ortalama uygunluk
- Popülasyon büyüklüğü
- En iyi uygunluk skoru 