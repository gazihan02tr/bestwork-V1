from app.database import engine, Base
from app.models import Kullanici

print("Tablolar oluşturuluyor...")
# Modellerde tanımladığımız her şeyi veritabanına fiziksel tablo olarak basar
Base.metadata.create_all(bind=engine)
print("✅ İşlem Başarılı: 'kullanicilar' tablosu PostgreSQL'de oluşturuldu.")