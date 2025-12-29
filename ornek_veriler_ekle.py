from app.database import SessionLocal
from app import models

db = SessionLocal()

# Örnek Kategoriler
kategoriler = [
    {"ad": "Elektronik", "aciklama": "Teknoloji ürünleri", "resim_url": "💻"},
    {"ad": "Giyim", "aciklama": "Kıyafet ve tekstil", "resim_url": "👔"},
    {"ad": "Kozmetik", "aciklama": "Güzellik ürünleri", "resim_url": "💄"},
    {"ad": "Ev & Yaşam", "aciklama": "Ev eşyaları", "resim_url": "🏠"},
]

for kat in kategoriler:
    db_kat = models.Kategori(**kat)
    db.add(db_kat)

db.commit()

# Örnek Ürünler
urunler = [
    {
        "ad": "Akıllı Telefon",
        "aciklama": "En son teknoloji ile donatılmış, yüksek performanslı akıllı telefon. 5G destekli, 128GB hafıza.",
        "fiyat": 12999.00,
        "indirimli_fiyat": 9999.00,
        "stok": 50,
        "kategori_id": 1,
        "resim_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
        "pv_degeri": 500
    },
    {
        "ad": "Kablosuz Kulaklık",
        "aciklama": "Aktif gürültü engelleme özellikli, 30 saat pil ömrü sunan premium kulaklık.",
        "fiyat": 2499.00,
        "indirimli_fiyat": 1999.00,
        "stok": 100,
        "kategori_id": 1,
        "resim_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "pv_degeri": 100
    },
    {
        "ad": "Erkek Gömlek",
        "aciklama": "Pamuklu, şık ve rahat kesim erkek gömleği. Günlük ve iş hayatınız için ideal.",
        "fiyat": 599.00,
        "stok": 75,
        "kategori_id": 2,
        "resim_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400",
        "pv_degeri": 30
    },
    {
        "ad": "Kadın Elbise",
        "aciklama": "Modern ve zarif tasarım, özel günler için mükemmel bir seçim.",
        "fiyat": 899.00,
        "indirimli_fiyat": 699.00,
        "stok": 40,
        "kategori_id": 2,
        "resim_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
        "pv_degeri": 40
    },
    {
        "ad": "Nemlendirici Krem",
        "aciklama": "Doğal içerikli, tüm cilt tiplerine uygun nemlendirici. 24 saat etki.",
        "fiyat": 349.00,
        "indirimli_fiyat": 249.00,
        "stok": 200,
        "kategori_id": 3,
        "resim_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400",
        "pv_degeri": 20
    },
    {
        "ad": "Makyaj Seti",
        "aciklama": "Profesyonel makyaj seti, 12 parça. Her duruma uygun renkler.",
        "fiyat": 1299.00,
        "indirimli_fiyat": 999.00,
        "stok": 60,
        "kategori_id": 3,
        "resim_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400",
        "pv_degeri": 80
    },
    {
        "ad": "Kahve Makinesi",
        "aciklama": "Otomatik kahve makinesi, 15 bar basınç, süt köpürtme özelliği.",
        "fiyat": 3499.00,
        "indirimli_fiyat": 2799.00,
        "stok": 30,
        "kategori_id": 4,
        "resim_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400",
        "pv_degeri": 150
    },
    {
        "ad": "Yastık Seti",
        "aciklama": "Anti-alerjik, ortopedik yastık seti. 2 adet, farklı sertlik seçenekleri.",
        "fiyat": 799.00,
        "indirimli_fiyat": 599.00,
        "stok": 120,
        "kategori_id": 4,
        "resim_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400",
        "pv_degeri": 35
    },
]

for urun_data in urunler:
    db_urun = models.Urun(**urun_data)
    db.add(db_urun)

db.commit()
db.close()

print("✅ Kategoriler ve ürünler başarıyla eklendi!")
print(f"📦 {len(kategoriler)} kategori")
print(f"🛍️ {len(urunler)} ürün")
