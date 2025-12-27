from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BestWork Binary Network Marketing")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.svg")

@app.get("/apple-touch-icon.png", include_in_schema=False)
async def apple_touch_icon():
    return FileResponse("static/favicon.svg")

@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
async def apple_touch_icon_precomposed():
    return FileResponse("static/favicon.svg")

@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
async def chrome_devtools():
    return {}

# Veritabanı bağlantı fonksiyonu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SİSTEM BAŞLANGIÇ AYARLARI ---
@app.on_event("startup")
def baslangic_ayarlarini_olustur():
    db = SessionLocal()
    try:
        # Genel Ayarlar
        varsayilan_ayarlar = {
            "kayit_pv": 100.0,
            "kayit_cv": 50.0,
            "referans_orani": 0.20,
            "eslesme_kazanc": 10.0,
            "matching_orani": 0.10,
            "kisa_kol_oran": 0.13
        } # <--- Bu parantezin burada olduğundan ve hizasından emin ol

        for anahtar, deger in varsayilan_ayarlar.items():
            db_ayar = db.query(models.Ayarlar).filter(models.Ayarlar.anahtar == anahtar).first()
            if not db_ayar:
                db.add(models.Ayarlar(anahtar=anahtar, deger=deger))

        # İlk 3 Nesil Otomatik
        varsayilan_nesiller = [{"no": 1, "o": 0.10}, {"no": 2, "o": 0.05}, {"no": 3, "o": 0.03}]
        for n in varsayilan_nesiller:
            db_nesil = db.query(models.NesilAyari).filter(models.NesilAyari.nesil_no == n["no"]).first()
            if not db_nesil:
                db.add(models.NesilAyari(nesil_no=n["no"], oran=n["o"]))
        
        db.commit()
    finally:
        db.close()

# --- YARDIMCI HESAPLAMA FONKSİYONU ---
def get_dashboard_data(user_id: int, db: Session):
    kullanici = db.query(models.Kullanici).filter(models.Kullanici.id == user_id).first()
    if not kullanici:
        return None

    def ekip_sayisini_bul(parent_id, kol=None):
        sorgu = db.query(models.Kullanici).filter(models.Kullanici.parent_id == parent_id)
        if kol:
            sorgu = sorgu.filter(models.Kullanici.kol == kol)
        ilk_katman = sorgu.all()
        toplam = len(ilk_katman)
        for alt in ilk_katman:
            toplam += ekip_sayisini_bul(alt.id)
        return toplam

    sol_ekip = ekip_sayisini_bul(user_id, "SOL")
    sag_ekip = ekip_sayisini_bul(user_id, "SAG")
    referanslar = db.query(models.Kullanici).filter(models.Kullanici.referans_id == user_id).count()

    return {
        "id": kullanici.id,
        "tam_ad": kullanici.tam_ad,
        "email": kullanici.email,
        "rutbe": getattr(kullanici, 'rutbe', 'Üye'),
        "toplam_cv": kullanici.toplam_cv,
        "mevcut_sol_pv": kullanici.sol_pv,
        "mevcut_sag_pv": kullanici.sag_pv,
        "toplam_sol_ekip": sol_ekip,
        "toplam_sag_ekip": sag_ekip,
        "referans_sayisi": referanslar
    }

# --- WEB PANEL ENDPOINTS ---

# KULLANICI DASHBOARD (Giydirilmiş Hali)
@app.get("/panel/{user_id}", response_class=HTMLResponse)
def dashboard_sayfasi(request: Request, user_id: int, db: Session = Depends(get_db)):
    ozet_verisi = get_dashboard_data(user_id, db)
    
    if not ozet_verisi:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")

    ekstre_verisi = db.query(models.CuzdanHareket).filter(
        models.CuzdanHareket.user_id == user_id
    ).order_by(models.CuzdanHareket.tarih.desc()).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "ozet": ozet_verisi, 
        "ekstre": ekstre_verisi,
        # Template içindeki değişken hatalarını önlemek için:
        "site_branding": {"site_name": "BestWork", "primary_color": "#7C3AED"},
        "t": lambda x: x, # Çeviri fonksiyonu desteği
        "current_user": {"name": ozet_verisi["tam_ad"], "id": ozet_verisi["id"]},
        "avatar_src": f"https://ui-avatars.com/api/?name={ozet_verisi['tam_ad']}&background=random"
    })

# ADMIN KONTROL SAYFASI
@app.get("/admin/kontrol", response_class=HTMLResponse)
def admin_ayar_sayfasi(request: Request, db: Session = Depends(get_db)):
    ayarlar = db.query(models.Ayarlar).all()
    nesiller = db.query(models.NesilAyari).order_by(models.NesilAyari.nesil_no).all()
    toplam_nesil_sayisi = len(nesiller)
    
    return templates.TemplateResponse("admin_ayarlar.html", {
        "request": request, 
        "ayarlar": ayarlar,
        "nesiller": nesiller,
        "toplam_nesil": toplam_nesil_sayisi
    })

# --- ADMIN İŞLEMLERİ ---

@app.post("/admin/ayarlar/guncelle")
def ayar_kaydet_form(anahtar: str = Form(...), deger: float = Form(...), db: Session = Depends(get_db)):
    db_ayar = db.query(models.Ayarlar).filter(models.Ayarlar.anahtar == anahtar).first()
    if db_ayar:
        db_ayar.deger = deger
        db.commit()
    return RedirectResponse(url="/admin/kontrol", status_code=303)

@app.post("/admin/nesil/ekle")
def nesil_ekle(nesil_no: int = Form(...), oran: float = Form(...), db: Session = Depends(get_db)):
    db_nesil = db.query(models.NesilAyari).filter(models.NesilAyari.nesil_no == nesil_no).first()
    if db_nesil:
        db_nesil.oran = oran
    else:
        db.add(models.NesilAyari(nesil_no=nesil_no, oran=oran))
    db.commit()
    return RedirectResponse(url="/admin/kontrol", status_code=303)

@app.get("/admin/nesil/sil/{nesil_id}")
def nesil_sil(nesil_id: int, db: Session = Depends(get_db)):
    db_nesil = db.query(models.NesilAyari).filter(models.NesilAyari.id == nesil_id).first()
    if db_nesil:
        db.delete(db_nesil)
        db.commit()
    return RedirectResponse(url="/admin/kontrol", status_code=303)

# --- API ENDPOINTS (Swagger için) ---

@app.post("/kayit/", response_model=schemas.KullaniciCevap)
def uye_kaydet_api(kullanici: schemas.KullaniciKayit, db: Session = Depends(get_db)):
    return crud.yeni_uye_kaydet(db=db, kullanici_verisi=kullanici)

@app.get("/api/dashboard/{user_id}")
def api_dashboard_getir(user_id: int, db: Session = Depends(get_db)):
    return get_dashboard_data(user_id, db)

# app/main.py içine ekle

@app.get("/api/tree/{user_id}")
def get_tree_data(user_id: int, db: Session = Depends(get_db)):
    def build_node(u_id):
        user = db.query(models.Kullanici).filter(models.Kullanici.id == u_id).first()
        if not user:
            return None
        
        # Alt üyeleri bul
        sol_uye = db.query(models.Kullanici).filter(models.Kullanici.parent_id == u_id, models.Kullanici.kol == "SOL").first()
        sag_uye = db.query(models.Kullanici).filter(models.Kullanici.parent_id == u_id, models.Kullanici.kol == "SAG").first()
        
        return {
            "name": user.tam_ad,
            "id": user.id,
            "pv": f"L: {user.sol_pv} | R: {user.sag_pv}",
            "children": [
                build_node(sol_uye.id) if sol_uye else {"name": "Boş", "id": None, "kol": "SOL", "parent": u_id},
                build_node(sag_uye.id) if sag_uye else {"name": "Boş", "id": None, "kol": "SAG", "parent": u_id}
            ]
        }
    
    return build_node(user_id)

@app.get("/panel/agac/{user_id}", response_class=HTMLResponse)
def tree_page(request: Request, user_id: int, db: Session = Depends(get_db)):
    # Temel template verileri
    return templates.TemplateResponse("tree.html", {
        "request": request,
        "user_id": user_id,
        "site_branding": {"site_name": "BestWork", "primary_color": "#7C3AED"},
        "t": lambda x: x
    })

# === E-TİCARET ENDPOINTS ===

# ANASAYFA
@app.get("/", response_class=HTMLResponse)
def anasayfa(request: Request, db: Session = Depends(get_db)):
    kategoriler = crud.kategorileri_listele(db)
    urunler = crud.urunleri_listele(db, limit=12)
    return templates.TemplateResponse("anasayfa.html", {
        "request": request,
        "kategoriler": kategoriler,
        "urunler": urunler
    })

# KATEGORİ SAYFASI
@app.get("/kategori/{kategori_id}", response_class=HTMLResponse)
def kategori_sayfasi(request: Request, kategori_id: int, db: Session = Depends(get_db)):
    kategori = crud.kategori_getir(db, kategori_id)
    if not kategori:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı!")
    
    urunler = crud.urunleri_listele(db, kategori_id=kategori_id)
    kategoriler = crud.kategorileri_listele(db)
    
    return templates.TemplateResponse("kategori.html", {
        "request": request,
        "kategori": kategori,
        "kategoriler": kategoriler,
        "urunler": urunler
    })

# ÜRÜN DETAY
@app.get("/urun/{urun_id}", response_class=HTMLResponse)
def urun_detay(request: Request, urun_id: int, db: Session = Depends(get_db)):
    urun = crud.urun_getir(db, urun_id)
    if not urun:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı!")
    
    return templates.TemplateResponse("urun_detay.html", {
        "request": request,
        "urun": urun
    })

# SEPET
@app.get("/sepet/{kullanici_id}", response_class=HTMLResponse)
def sepet_sayfasi(request: Request, kullanici_id: int, db: Session = Depends(get_db)):
    sepet = crud.sepet_detayi_getir(db, kullanici_id)
    return templates.TemplateResponse("sepet.html", {
        "request": request,
        "sepet": sepet,
        "kullanici_id": kullanici_id
    })

# API: Sepete Ürün Ekle
@app.post("/api/sepet/{kullanici_id}/ekle")
def sepete_ekle_api(kullanici_id: int, urun_id: int = Form(...), adet: int = Form(1), db: Session = Depends(get_db)):
    crud.sepete_urun_ekle(db, kullanici_id, urun_id, adet)
    return RedirectResponse(url=f"/sepet/{kullanici_id}", status_code=303)

# API: Sepetten Ürün Çıkar
@app.get("/api/sepet/{kullanici_id}/cikar/{sepet_urun_id}")
def sepetten_cikar_api(kullanici_id: int, sepet_urun_id: int, db: Session = Depends(get_db)):
    crud.sepetten_urun_cikar(db, kullanici_id, sepet_urun_id)
    return RedirectResponse(url=f"/sepet/{kullanici_id}", status_code=303)

# API: Sipariş Oluştur
@app.post("/api/siparis/{kullanici_id}/olustur")
def siparis_olustur_api(kullanici_id: int, adres: str = Form(...), db: Session = Depends(get_db)):
    siparis = crud.siparis_olustur(db, kullanici_id, adres)
    return RedirectResponse(url=f"/siparisler/{kullanici_id}", status_code=303)

# SİPARİŞLERİM
@app.get("/siparisler/{kullanici_id}", response_class=HTMLResponse)
def siparisler_sayfasi(request: Request, kullanici_id: int, db: Session = Depends(get_db)):
    siparisler = crud.kullanici_siparislerini_getir(db, kullanici_id)
    return templates.TemplateResponse("siparisler.html", {
        "request": request,
        "siparisler": siparisler,
        "kullanici_id": kullanici_id
    })

# ADMİN: Ürün Ekleme
@app.get("/admin/urun/ekle", response_class=HTMLResponse)
def admin_urun_ekle_form(request: Request, db: Session = Depends(get_db)):
    kategoriler = crud.kategorileri_listele(db)
    return templates.TemplateResponse("admin_urun_ekle.html", {
        "request": request,
        "kategoriler": kategoriler
    })

@app.post("/admin/urun/ekle")
def admin_urun_ekle(
    ad: str = Form(...),
    aciklama: str = Form(""),
    fiyat: float = Form(...),
    indirimli_fiyat: float = Form(None),
    stok: int = Form(0),
    kategori_id: int = Form(None),
    resim_url: str = Form(""),
    pv_degeri: int = Form(0),
    db: Session = Depends(get_db)
):
    urun_data = schemas.UrunOlustur(
        ad=ad,
        aciklama=aciklama,
        fiyat=fiyat,
        indirimli_fiyat=indirimli_fiyat if indirimli_fiyat else None,
        stok=stok,
        kategori_id=kategori_id if kategori_id else None,
        resim_url=resim_url,
        pv_degeri=pv_degeri
    )
    crud.urun_olustur(db, urun_data)
    return RedirectResponse(url="/admin/urunler", status_code=303)

# ADMİN: Ürün Listesi
@app.get("/admin/urunler", response_class=HTMLResponse)
def admin_urunler(request: Request, db: Session = Depends(get_db)):
    urunler = crud.urunleri_listele(db, limit=1000)
    return templates.TemplateResponse("admin_urunler.html", {
        "request": request,
        "urunler": urunler
    })