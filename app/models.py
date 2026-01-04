from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float, DateTime, Text
from datetime import datetime
from zoneinfo import ZoneInfo
import enum
from .database import Base

def get_turkey_time():
    return datetime.now(ZoneInfo("Europe/Istanbul"))

class KolPozisyon(str, enum.Enum):
    SAG = "SAG"
    SOL = "SOL"

class Kullanici(Base):
    __tablename__ = "kullanicilar"

    id = Column(Integer, primary_key=True, index=True)
    uye_no = Column(String(20), unique=True, index=True) # 90 ile başlayan özel ID
    tam_ad = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    telefon = Column(String(20))
    sifre = Column(String(255))
    rutbe = Column(String, default="Distribütör")
    profil_resmi = Column(String, nullable=True)

    # Kişisel Bilgiler
    tc_no = Column(String(11), nullable=True)
    dogum_tarihi = Column(DateTime(timezone=True), nullable=True)
    cinsiyet = Column(String(10), nullable=True) # KADIN / ERKEK
    uyelik_turu = Column(String(20), default="Bireysel") # Bireysel / Kurumsal
    
    # Adres Bilgileri
    ulke = Column(String(50), default="Türkiye")
    il = Column(String(50), nullable=True)
    ilce = Column(String(50), nullable=True)
    mahalle = Column(String(100), nullable=True)
    adres = Column(Text, nullable=True)
    posta_kodu = Column(String(10), nullable=True)

    # Vergi Bilgileri (Kurumsal için)
    vergi_dairesi = Column(String(100), nullable=True)
    vergi_no = Column(String(20), nullable=True)
    
    # Bağlantılar
    referans_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=True)
    kol = Column(Enum(KolPozisyon), nullable=True)

    # PV - CV Sistemi
    sol_pv = Column(Integer, default=0)
    sag_pv = Column(Integer, default=0)
    toplam_cv = Column(Float, default=0.0)
    toplam_sol_pv = Column(Integer, default=0)
    toplam_sag_pv = Column(Integer, default=0)

    kayit_tarihi = Column(DateTime(timezone=True), default=get_turkey_time)
    yerlestirme_tarihi = Column(DateTime(timezone=True), nullable=True)

class Ayarlar(Base):
    __tablename__ = "ayarlar"

    id = Column(Integer, primary_key=True, index=True)
    anahtar = Column(String, unique=True, index=True) # Örn: 'referans_orani'
    deger = Column(Float) # Örn: 0.40

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean

class CuzdanHareket(Base):
    __tablename__ = "cuzdan_hareketleri"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    miktar = Column(Float)
    islem_tipi = Column(String) # "REFERANS", "ESLESME", "LIDERLIK"
    aciklama = Column(String)
    tarih = Column(DateTime(timezone=True), default=get_turkey_time)

class IletisimMesaji(Base):
    __tablename__ = "iletisim_mesajlari"

    id = Column(Integer, primary_key=True, index=True)
    ad_soyad = Column(String)
    email = Column(String)
    konu = Column(String)
    mesaj = Column(Text)
    takip_no = Column(String, unique=True, index=True)
    tarih = Column(DateTime(timezone=True), default=get_turkey_time)
    durum = Column(String, default="Beklemede") # Beklemede, Okundu, Cevaplandı

class NesilAyari(Base):
    __tablename__ = "nesil_ayarlari"
    id = Column(Integer, primary_key=True, index=True)
    nesil_no = Column(Integer)  # 1, 2, 3...
    oran = Column(Float)        # 0.10, 0.05...

class Varis(Base):
    __tablename__ = "varisler"

    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"))
    ad_soyad = Column(String(100), nullable=False)
    tc = Column(String(11), nullable=False)
    telefon = Column(String(20))
    email = Column(String(100))
    yakinlik = Column(String(50))
    adres = Column(Text)
    olusturma_tarihi = Column(DateTime(timezone=True), default=get_turkey_time)

# E-TİCARET MODELLERİ

class Kategori(Base):
    __tablename__ = "kategoriler"
    
    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(100), nullable=False)
    aciklama = Column(Text)
    resim_url = Column(String(500))
    aktif = Column(Boolean, default=True)
    olusturma_tarihi = Column(DateTime(timezone=True), default=get_turkey_time)

class Urun(Base):
    __tablename__ = "urunler"
    
    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(200), nullable=False, index=True)
    aciklama = Column(Text)
    fiyat = Column(Float, nullable=False)
    indirimli_fiyat = Column(Float, nullable=True)
    stok = Column(Integer, default=0)
    kategori_id = Column(Integer, ForeignKey("kategoriler.id"))
    resim_url = Column(String(500))
    pv_degeri = Column(Integer, default=0)  # Network marketing için PV puanı
    aktif = Column(Boolean, default=True)
    olusturma_tarihi = Column(DateTime(timezone=True), default=get_turkey_time)

class Sepet(Base):
    __tablename__ = "sepetler"
    
    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"))
    olusturma_tarihi = Column(DateTime(timezone=True), default=get_turkey_time)
    guncelleme_tarihi = Column(DateTime(timezone=True), default=get_turkey_time, onupdate=get_turkey_time)

class SepetUrun(Base):
    __tablename__ = "sepet_urunler"
    
    id = Column(Integer, primary_key=True, index=True)
    sepet_id = Column(Integer, ForeignKey("sepetler.id"))
    urun_id = Column(Integer, ForeignKey("urunler.id"))
    adet = Column(Integer, default=1)
    ekleme_tarihi = Column(DateTime(timezone=True), default=get_turkey_time)

class Siparis(Base):
    __tablename__ = "siparisler"
    
    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"))
    toplam_tutar = Column(Float, nullable=False)
    toplam_pv = Column(Integer, default=0)
    durum = Column(String(50), default="BEKLEMEDE")  # BEKLEMEDE, ONAYLANDI, KARGODA, TESLIM_EDILDI
    adres = Column(Text)
    olusturma_tarihi = Column(DateTime(timezone=True), default=get_turkey_time)

class SiparisUrun(Base):
    __tablename__ = "siparis_urunler"
    
    id = Column(Integer, primary_key=True, index=True)
    siparis_id = Column(Integer, ForeignKey("siparisler.id"))
    urun_id = Column(Integer, ForeignKey("urunler.id"))
    urun_adi = Column(String(200))
    adet = Column(Integer)
    birim_fiyat = Column(Float)
    pv_degeri = Column(Integer)
class BankaBilgisi(Base):
    __tablename__ = "banka_bilgileri"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("kullanicilar.id"))
    hesap_sahibi = Column(String(100))
    banka_adi = Column(String(100))
    iban = Column(String(34))
    swift_kodu = Column(String(20), nullable=True)
    guncelleme_tarihi = Column(DateTime(timezone=True), default=get_turkey_time, onupdate=get_turkey_time)
