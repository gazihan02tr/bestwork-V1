from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from fastapi import HTTPException
from datetime import datetime
import uuid

# --- YARDIMCI: CÜZDAN HAREKETİ KAYDET ---
def log_yaz(db: Session, user_id: int, miktar: float, tip: str, mesaj: str):
    yeni_log = models.CuzdanHareket(
        user_id=user_id,
        miktar=miktar,
        islem_tipi=tip,
        aciklama=mesaj
    )
    db.add(yeni_log)
    db.commit()

# --- 1. FONKSİYON: BOŞ YER BULUCU ---
def en_alt_bos_yeri_bul(db: Session, parent_id: int, tercih_kol: str):
    """
    Kullanıcı sadece seçtiği kolun (SOL veya SAĞ) en dış hattına kayıt yapabilir.
    İç kollara (inner leg) kayıt yapılmasına izin vermez.
    """
    # Mevcut parent'ın altında, seçilen kolda (SOL veya SAĞ) biri var mı?
    mevcut_uye = db.query(models.Kullanici).filter(
        models.Kullanici.parent_id == parent_id,
        models.Kullanici.kol == tercih_kol
    ).first()

    if not mevcut_uye:
        # Eğer o kol boşsa, burası kayıt için doğru yerdir.
        return parent_id
    
    # EĞER DOLUYSA: 
    # İçeriye bakma, sadece aynı kol (tercih_kol) üzerinden en aşağı git!
    return en_alt_bos_yeri_bul(db, mevcut_uye.id, tercih_kol)

# --- 2. FONKSİYON: PUAN DAĞITIM MOTORU ---
def ekonomiyi_tetikle(db: Session, baslangic_id: int, satis_pv: int, satis_cv: float):
    mevcut_uye = db.query(models.Kullanici).filter(models.Kullanici.id == baslangic_id).first()
    if not mevcut_uye or not mevcut_uye.parent_id:
        return

    ust_uye = db.query(models.Kullanici).filter(models.Kullanici.id == mevcut_uye.parent_id).first()
    if ust_uye:
        # PV değerleri None ise 0 olarak başlat
        if ust_uye.sol_pv is None: ust_uye.sol_pv = 0
        if ust_uye.sag_pv is None: ust_uye.sag_pv = 0

        # Kol kontrolü (Enum veya String uyumluluğu)
        is_sol = (mevcut_uye.kol == models.KolPozisyon.SOL) or (str(mevcut_uye.kol) == "SOL")

        if is_sol:
            ust_uye.sol_pv += satis_pv
        else:
            ust_uye.sag_pv += satis_pv
        
        db.commit()
        eslesme_kontrol_et(db, ust_uye.id)
        ekonomiyi_tetikle(db, ust_uye.id, satis_pv, satis_cv)

def yeni_uye_no_olustur(db: Session):
    en_son = db.query(func.max(models.Kullanici.uye_no)).filter(models.Kullanici.uye_no.like("90%")).scalar()
    if en_son:
        return str(int(en_son) + 1)
    return "900000001"

# --- 3. ANA FONKSİYON: KAYIT ---
def yeni_uye_kaydet(db: Session, kullanici_verisi: schemas.KullaniciKayit):
    # 1. E-posta Kontrolü
    if db.query(models.Kullanici).filter(models.Kullanici.email == kullanici_verisi.email).first():
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayıtlı!")

    # 2. TC Kimlik No Kontrolü
    if kullanici_verisi.tc_no:
        mevcut_tc = db.query(models.Kullanici).filter(models.Kullanici.tc_no == kullanici_verisi.tc_no).first()
        if mevcut_tc:
            raise HTTPException(status_code=400, detail="Bu TC Kimlik Numarası ile daha önce kayıt olunmuş!")

    # 3. Telefon Numarası Kontrolü
    if db.query(models.Kullanici).filter(models.Kullanici.telefon == kullanici_verisi.telefon).first():
        raise HTTPException(status_code=400, detail="Bu telefon numarası zaten kayıtlı!")

    # ARTIK OTOMATİK YERLEŞTİRME YOK
    # Yeni üye parent_id=None ve kol=None olarak kaydedilir (Bekleme Odası)
    
    yeni_no = yeni_uye_no_olustur(db)
    
    # Tarih formatını düzeltme (String gelirse)
    dogum_tarihi_val = None
    if kullanici_verisi.dogum_tarihi:
        try:
            dogum_tarihi_val = datetime.strptime(kullanici_verisi.dogum_tarihi, "%Y-%m-%d")
        except:
            pass

    yeni_uye = models.Kullanici(
        tam_ad=kullanici_verisi.tam_ad,
        email=kullanici_verisi.email,
        telefon=kullanici_verisi.telefon,
        sifre=kullanici_verisi.sifre,
        referans_id=kullanici_verisi.referans_id,
        parent_id=None, # AĞAÇTA YERİ YOK (BEKLEMEDE)
        kol=None,       # KOLU YOK (BEKLEMEDE)
        uye_no=yeni_no,
        # Yeni Alanlar
        tc_no=kullanici_verisi.tc_no,
        dogum_tarihi=dogum_tarihi_val,
        cinsiyet=kullanici_verisi.cinsiyet,
        uyelik_turu=kullanici_verisi.uyelik_turu,
        ulke=kullanici_verisi.ulke,
        il=kullanici_verisi.il,
        ilce=kullanici_verisi.ilce,
        mahalle=kullanici_verisi.mahalle,
        adres=kullanici_verisi.adres,
        posta_kodu=kullanici_verisi.posta_kodu,
        vergi_dairesi=kullanici_verisi.vergi_dairesi,
        vergi_no=kullanici_verisi.vergi_no
    )
    
    try:
        db.add(yeni_uye)
        db.commit()
        db.refresh(yeni_uye)

        # NOT: Puan dağıtımı ve referans bonusu artık üye ağaca yerleştirildiğinde yapılacak.
        # Burada sadece kayıt işlemi yapılıyor.

        return yeni_uye
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")

# --- YENİ: ÜYEYİ AĞACA YERLEŞTİR ---
def uyeyi_agaca_yerlestir(db: Session, uye_id: int, parent_id: int, kol: str):
    uye = db.query(models.Kullanici).filter(models.Kullanici.id == uye_id).first()
    if not uye:
        raise HTTPException(status_code=404, detail="Üye bulunamadı")
    
    if uye.parent_id is not None:
        raise HTTPException(status_code=400, detail="Üye zaten ağaca yerleştirilmiş")

    # Hedef yerin boş olup olmadığını kontrol et
    hedef_yer_dolu = db.query(models.Kullanici).filter(
        models.Kullanici.parent_id == parent_id,
        models.Kullanici.kol == kol
    ).first()
    
    if hedef_yer_dolu:
        raise HTTPException(status_code=400, detail="Seçilen pozisyon dolu!")

    uye.parent_id = parent_id
    uye.kol = kol
    db.commit()
    
    # Puanları ve Bonusları Şimdi İşle
    kayit_pv = ayar_getir(db, "kayit_pv", 100.0)
    kayit_cv = ayar_getir(db, "kayit_cv", 50.0)
    ref_orani = ayar_getir(db, "referans_orani", 0.40)

    ekonomiyi_tetikle(db, uye.id, satis_pv=int(kayit_pv), satis_cv=kayit_cv)
    referans_bonusu_ode(db, uye.referans_id, (kayit_cv * ref_orani), uye.tam_ad)
    
    return True

# --- 4. GÜNCELLENEN EŞLEŞME: %13 KISA KOL MANTIĞI ---
def eslesme_kontrol_et(db: Session, kullanici_id: int):
    kullanici = db.query(models.Kullanici).filter(models.Kullanici.id == kullanici_id).first()
    
    # PV değerleri None ise 0 olarak başlat
    if kullanici.sol_pv is None: kullanici.sol_pv = 0
    if kullanici.sag_pv is None: kullanici.sag_pv = 0
    
    # Her iki kolda da puan birikmiş mi?
    if kullanici.sol_pv > 0 and kullanici.sag_pv > 0:
        # Kısa kolu (ödenecek puanı) belirle
        odenecek_puan = min(kullanici.sol_pv, kullanici.sag_pv)
        
        # Ayarlardan %13 oranını çek (admin panelinden güncellenebilir)
        odeme_orani = ayar_getir(db, "kisa_kol_oran", 0.13)
        
        # Kazanç = Kısa Kol Cirosu * Oran
        kazanc = odenecek_puan * odeme_orani
        
        # Bakiyeyi güncelle ve puanları kollardan düş (Dengeleme)
        if kullanici.toplam_cv is None: kullanici.toplam_cv = 0.0
        kullanici.toplam_cv += kazanc
        kullanici.sol_pv -= odenecek_puan
        kullanici.sag_pv -= odenecek_puan
        
        db.commit()
        
        log_yaz(db, kullanici_id, kazanc, "ESLESME", 
                f"Kısa kol cirosu ({odenecek_puan} PV) üzerinden %{int(odeme_orani*100)} kazanç.")
        
        # Nesil Geliri (Matching) Dağıtımı
        nesil_geliri_dagit(db, kullanici.id, kazanc, 1)

def nesil_geliri_dagit(db: Session, alt_uye_id: int, kazanilan_miktar: float, nesil: int):
    """
    Sponsor hattı boyunca yukarı çıkar ve her nesle tanımlı oranını öder.
    """
    # 1. Bu nesil için bir ayar var mı?
    ayar = db.query(models.NesilAyari).filter(models.NesilAyari.nesil_no == nesil).first()
    if not ayar:
        return # Ayar yoksa daha yukarı ödeme yapılmaz.

    # 2. Alt üyenin sponsorunu (liderini) bul
    alt_uye = db.query(models.Kullanici).filter(models.Kullanici.id == alt_uye_id).first()
    if not alt_uye or not alt_uye.referans_id:
        return # Sponsor yoksa bitti.

    lider = db.query(models.Kullanici).filter(models.Kullanici.id == alt_uye.referans_id).first()
    if lider:
        bonus = kazanilan_miktar * ayar.oran
        lider.toplam_cv += bonus
        db.commit()
        
        log_yaz(db, lider.id, bonus, "LIDERLIK", f"{nesil}. Nesil Primi ({alt_uye.tam_ad} kazancından)")
        
        # 3. BİR ÜST NESLE GEÇ (Recursive)
        nesil_geliri_dagit(db, lider.id, kazanilan_miktar, nesil + 1)

def referans_bonusu_ode(db: Session, sponsor_id: int, prim_miktari: float, yeni_uye_adi: str):
    sponsor = db.query(models.Kullanici).filter(models.Kullanici.id == sponsor_id).first()
    if sponsor:
        sponsor.toplam_cv += prim_miktari
        db.commit()
        log_yaz(db, sponsor_id, prim_miktari, "REFERANS", f"Yeni kayıt: {yeni_uye_adi}")

def ayar_getir(db: Session, anahtar: str, varsayilan: float):
    db_ayar = db.query(models.Ayarlar).filter(models.Ayarlar.anahtar == anahtar).first()
    if not db_ayar:
        yeni_ayar = models.Ayarlar(anahtar=anahtar, deger=varsayilan)
        db.add(yeni_ayar)
        db.commit()
        return varsayilan
    return db_ayar.deger

# === E-TİCARET CRUD FONKSİYONLARI ===

# Kategori İşlemleri
def kategori_olustur(db: Session, kategori: schemas.KategoriOlustur):
    db_kategori = models.Kategori(**kategori.dict())
    db.add(db_kategori)
    db.commit()
    db.refresh(db_kategori)
    return db_kategori

def kategorileri_listele(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Kategori).filter(models.Kategori.aktif == True).offset(skip).limit(limit).all()

def kategori_getir(db: Session, kategori_id: int):
    return db.query(models.Kategori).filter(models.Kategori.id == kategori_id).first()

# Ürün İşlemleri
def urun_olustur(db: Session, urun: schemas.UrunOlustur):
    db_urun = models.Urun(**urun.dict())
    db.add(db_urun)
    db.commit()
    db.refresh(db_urun)
    return db_urun

def urunleri_listele(db: Session, kategori_id: int = None, skip: int = 0, limit: int = 100):
    sorgu = db.query(models.Urun).filter(models.Urun.aktif == True)
    if kategori_id:
        sorgu = sorgu.filter(models.Urun.kategori_id == kategori_id)
    return sorgu.offset(skip).limit(limit).all()

def urun_getir(db: Session, urun_id: int):
    return db.query(models.Urun).filter(models.Urun.id == urun_id).first()

def urun_guncelle(db: Session, urun_id: int, urun: schemas.UrunGuncelle):
    db_urun = db.query(models.Urun).filter(models.Urun.id == urun_id).first()
    if db_urun:
        for key, value in urun.dict(exclude_unset=True).items():
            setattr(db_urun, key, value)
        db.commit()
        db.refresh(db_urun)
    return db_urun

# Sepet İşlemleri
def sepet_getir_veya_olustur(db: Session, kullanici_id: int):
    sepet = db.query(models.Sepet).filter(models.Sepet.kullanici_id == kullanici_id).first()
    if not sepet:
        sepet = models.Sepet(kullanici_id=kullanici_id)
        db.add(sepet)
        db.commit()
        db.refresh(sepet)
    return sepet

def sepete_urun_ekle(db: Session, kullanici_id: int, urun_id: int, adet: int = 1):
    sepet = sepet_getir_veya_olustur(db, kullanici_id)
    
    # Ürünün zaten sepette olup olmadığını kontrol et
    mevcut = db.query(models.SepetUrun).filter(
        models.SepetUrun.sepet_id == sepet.id,
        models.SepetUrun.urun_id == urun_id
    ).first()
    
    if mevcut:
        mevcut.adet += adet
    else:
        yeni_sepet_urun = models.SepetUrun(sepet_id=sepet.id, urun_id=urun_id, adet=adet)
        db.add(yeni_sepet_urun)
    
    db.commit()
    return sepet

def sepet_detayi_getir(db: Session, kullanici_id: int):
    sepet = sepet_getir_veya_olustur(db, kullanici_id)
    
    sepet_urunler = db.query(models.SepetUrun).filter(models.SepetUrun.sepet_id == sepet.id).all()
    
    urunler = []
    toplam_fiyat = 0
    toplam_adet = 0
    
    for sepet_urun in sepet_urunler:
        urun = db.query(models.Urun).filter(models.Urun.id == sepet_urun.urun_id).first()
        if urun:
            fiyat = urun.indirimli_fiyat if urun.indirimli_fiyat else urun.fiyat
            urunler.append({
                "id": sepet_urun.id,
                "urun": urun,
                "adet": sepet_urun.adet,
                "toplam": fiyat * sepet_urun.adet
            })
            toplam_fiyat += fiyat * sepet_urun.adet
            toplam_adet += sepet_urun.adet
    
    return {
        "id": sepet.id,
        "urunler": urunler,
        "toplam_fiyat": toplam_fiyat,
        "toplam_adet": toplam_adet
    }

def sepetten_urun_cikar(db: Session, kullanici_id: int, sepet_urun_id: int):
    sepet = sepet_getir_veya_olustur(db, kullanici_id)
    
    sepet_urun = db.query(models.SepetUrun).filter(
        models.SepetUrun.id == sepet_urun_id,
        models.SepetUrun.sepet_id == sepet.id
    ).first()
    
    if sepet_urun:
        db.delete(sepet_urun)
        db.commit()
    
    return True

def sepeti_temizle(db: Session, kullanici_id: int):
    sepet = sepet_getir_veya_olustur(db, kullanici_id)
    db.query(models.SepetUrun).filter(models.SepetUrun.sepet_id == sepet.id).delete()
    db.commit()
    return True

# Sipariş İşlemleri
def siparis_olustur(db: Session, kullanici_id: int, adres: str):
    sepet_detay = sepet_detayi_getir(db, kullanici_id)
    
    if not sepet_detay["urunler"]:
        raise HTTPException(status_code=400, detail="Sepetiniz boş!")
    
    # Toplam PV hesapla
    toplam_pv = 0
    for item in sepet_detay["urunler"]:
        toplam_pv += item["urun"].pv_degeri * item["adet"]
    
    # Sipariş oluştur
    siparis = models.Siparis(
        kullanici_id=kullanici_id,
        toplam_tutar=sepet_detay["toplam_fiyat"],
        toplam_pv=toplam_pv,
        adres=adres
    )
    db.add(siparis)
    db.commit()
    db.refresh(siparis)
    
    # Sipariş ürünlerini kaydet
    for item in sepet_detay["urunler"]:
        urun = item["urun"]
        fiyat = urun.indirimli_fiyat if urun.indirimli_fiyat else urun.fiyat
        
        siparis_urun = models.SiparisUrun(
            siparis_id=siparis.id,
            urun_id=urun.id,
            urun_adi=urun.ad,
            adet=item["adet"],
            birim_fiyat=fiyat,
            pv_degeri=urun.pv_degeri
        )
        db.add(siparis_urun)
    
    # Network marketing ekonomisini tetikle
    if toplam_pv > 0:
        ekonomiyi_tetikle(db, kullanici_id, toplam_pv, sepet_detay["toplam_fiyat"])
    
    # Sepeti temizle
    sepeti_temizle(db, kullanici_id)
    
    db.commit()
    return siparis

def kullanici_siparislerini_getir(db: Session, kullanici_id: int):
    return db.query(models.Siparis).filter(
        models.Siparis.kullanici_id == kullanici_id
    ).order_by(models.Siparis.olusturma_tarihi.desc()).all()


def kariyer_guncelle(db: Session, kullanici_id: int):
    kullanici = db.query(models.Kullanici).filter(models.Kullanici.id == kullanici_id).first()
    if not kullanici:
        return

    # Senin belirlediğin kısa kol ciro (PV) baremleri
    ciro = min(kullanici.sol_pv, kullanici.sag_pv)
    
    eski_rutbe = kullanici.rutbe
    yeni_rutbe = "Distributor"

    # Kariyer Basamakları (Tam Liste)
    if ciro >= 25000000:   yeni_rutbe = "Triple President"
    elif ciro >= 10000000: yeni_rutbe = "Double President"
    elif ciro >= 5000000:  yeni_rutbe = "President"
    elif ciro >= 2500000:  yeni_rutbe = "Triple Diamond"
    elif ciro >= 1000000:  yeni_rutbe = "Double Diamond"
    elif ciro >= 500000:   yeni_rutbe = "Diamond"
    elif ciro >= 250000:   yeni_rutbe = "Emerald"
    elif ciro >= 100000:   yeni_rutbe = "Ruby"
    elif ciro >= 50000:    yeni_rutbe = "Sapphire"
    elif ciro >= 15000:    yeni_rutbe = "Pearl"
    elif ciro >= 5000:     yeni_rutbe = "Platinum"
    else:                  yeni_rutbe = "Distribütör"

    if eski_rutbe != yeni_rutbe:
        kullanici.rutbe = yeni_rutbe
        db.commit()
        # İsteğe bağlı: Rütbe değişimini günlüğe kaydet
        log_yaz(db, kullanici.id, 0, "RANK_UP", f"Yeni Kariyer: {yeni_rutbe}")

# --- İLETİŞİM MESAJI OLUŞTUR ---
def create_iletisim_mesaji(db: Session, mesaj: schemas.IletisimCreate):
    takip_no = str(uuid.uuid4().hex[:8]).upper()
    db_mesaj = models.IletisimMesaji(
        ad_soyad=mesaj.ad_soyad,
        email=mesaj.email,
        konu=mesaj.konu,
        mesaj=mesaj.mesaj,
        takip_no=takip_no
    )
    db.add(db_mesaj)
    db.commit()
    db.refresh(db_mesaj)
    return db_mesaj

def sifre_guncelle(db: Session, user_id: int, yeni_sifre: str):
    user = db.query(models.Kullanici).filter(models.Kullanici.id == user_id).first()
    if user:
        user.sifre = yeni_sifre
        db.commit()
        return True
    return False

# --- VARİS İŞLEMLERİ ---
def varis_olustur(db: Session, varis: schemas.VarisCreate, kullanici_id: int):
    db_varis = models.Varis(**varis.dict(), kullanici_id=kullanici_id)
    db.add(db_varis)
    db.commit()
    db.refresh(db_varis)
    return db_varis

def varisleri_getir(db: Session, kullanici_id: int):
    return db.query(models.Varis).filter(models.Varis.kullanici_id == kullanici_id).all()

def varis_guncelle(db: Session, varis_id: int, varis: schemas.VarisUpdate, kullanici_id: int):
    db_varis = db.query(models.Varis).filter(models.Varis.id == varis_id, models.Varis.kullanici_id == kullanici_id).first()
    if db_varis:
        for key, value in varis.dict(exclude_unset=True).items():
            setattr(db_varis, key, value)
        db.commit()
        db.refresh(db_varis)
    return db_varis

def varis_sil(db: Session, varis_id: int, kullanici_id: int):
    db_varis = db.query(models.Varis).filter(models.Varis.id == varis_id, models.Varis.kullanici_id == kullanici_id).first()
    if db_varis:
        db.delete(db_varis)
        db.commit()
        return True
    return False
