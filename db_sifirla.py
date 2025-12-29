from app.database import engine
from app.models import Base

def veritabani_sifirla():
    print("⚠️  Veritabanı sıfırlanıyor...")
    
    # Tüm tabloları sil
    Base.metadata.drop_all(bind=engine)
    print("✅ Tüm tablolar silindi.")
    
    # Tabloları yeniden oluştur
    Base.metadata.create_all(bind=engine)
    print("✅ Tablolar yeniden oluşturuldu.")

if __name__ == "__main__":
    onay = input("TÜM VERİLER SİLİNECEK! Emin misiniz? (e/h): ")
    if onay.lower() == 'e':
        veritabani_sifirla()
    else:
        print("İşlem iptal edildi.")
