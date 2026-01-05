from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, HTMLResponse
from app import models, crud, schemas
from app.dependencies import get_db, templates

router = APIRouter()

# --- BESTSOFT ADMIN GİRİŞ ---
@router.get("/bestsoft", response_class=HTMLResponse)
async def bestsoft_login_page(request: Request):
    return templates.TemplateResponse("bestsoft_login.html", {"request": request})

@router.post("/bestsoft/login")
async def bestsoft_login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(models.Admin.kullanici_adi == username).first()
    if not admin or admin.sifre != password:
        return templates.TemplateResponse("bestsoft_login.html", {"request": request, "error": "Geçersiz Kullanıcı Adı veya Şifre"})
    
    response = RedirectResponse(url="/admin/kontrol", status_code=303)
    response.set_cookie(key="admin_user", value=username)
    return response


# ADMIN KONTROL SAYFASI
@router.get("/admin/kontrol", response_class=HTMLResponse)
def admin_ayar_sayfasi(request: Request, db: Session = Depends(get_db)):
    admin_user = request.cookies.get("admin_user")
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
    
    nesiller = db.query(models.NesilAyari).order_by(models.NesilAyari.nesil_no).all()
    # Key-Value Ayarlar (eskiden kalma)
    kv_ayarlar = db.query(models.Ayarlar).all()
    # Yeni Site Ayarları (Footer vs)
    site_ayarlari = db.query(models.SiteAyarlari).first()
    if not site_ayarlari:
        site_ayarlari = models.SiteAyarlari()
        db.add(site_ayarlari)
        db.commit()
    
    return templates.TemplateResponse("admin_ayarlar.html", {
        "request": request,
        "nesiller": nesiller,
        "toplam_nesil": len(nesiller),
        "ayarlar": kv_ayarlar,
        "site_ayarlar": site_ayarlari
    })

# --- ADMIN İŞLEMLERİ ---

# 1. Key-Value Ayarları Güncelle (Tek tek)
@router.post("/admin/kv-ayarlar/guncelle")
def admin_kv_ayar_guncelle(
    anahtar: str = Form(...),
    deger: float = Form(...),
    db: Session = Depends(get_db)
):
    print(f"DEBUG: KV Update -> {anahtar} = {deger}")
    ayar = db.query(models.Ayarlar).filter(models.Ayarlar.anahtar == anahtar).first()
    if ayar:
        ayar.deger = deger
        db.commit()
    return RedirectResponse(url="/admin/kontrol", status_code=303)

# 2. Genel Site Ayarları Güncelle (Toplu)
@router.post("/admin/site-ayarlari/guncelle")
def admin_site_ayarlari_guncelle(
    site_basligi: str = Form(...),
    min_cekime_limiti: float = Form(...),
    footer_baslik: str = Form(None),
    footer_aciklama: str = Form(None),
    footer_copyright: str = Form(None),
    iletisim_email: str = Form(None),
    iletisim_telefon: str = Form(None),
    db: Session = Depends(get_db)
):
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
    
    ayarlar.site_basligi = site_basligi
    ayarlar.min_cekime_limiti = min_cekime_limiti
    ayarlar.footer_baslik = footer_baslik
    ayarlar.footer_aciklama = footer_aciklama
    ayarlar.footer_copyright = footer_copyright
    ayarlar.iletisim_email = iletisim_email
    ayarlar.iletisim_telefon = iletisim_telefon
    
    db.commit()
    
    return RedirectResponse(url="/admin/kontrol", status_code=303)

@router.post("/admin/nesil/ekle")
def admin_nesil_ekle(
    ad: str = Form(...),
    yuzde: float = Form(...),
    derinlik: int = Form(...),
    db: Session = Depends(get_db)
):
    yeni_nesil = models.Nesil(ad=ad, yuzde=yuzde, derinlik=derinlik)
    db.add(yeni_nesil)
    db.commit()
    return RedirectResponse(url="/admin/kontrol", status_code=303)

@router.get("/admin/nesil/sil/{nesil_id}")
def admin_nesil_sil(nesil_id: int, db: Session = Depends(get_db)):
    db.query(models.Nesil).filter(models.Nesil.id == nesil_id).delete()
    db.commit()
    return RedirectResponse(url="/admin/kontrol", status_code=303)

# ADMİN: Ürün Ekleme
@router.get("/admin/urun/ekle", response_class=HTMLResponse)
def admin_urun_ekle_form(request: Request, db: Session = Depends(get_db)):
    kategoriler = crud.kategorileri_listele(db)
    return templates.TemplateResponse("admin_urun_ekle.html", {
        "request": request,
        "kategoriler": kategoriler
    })

@router.post("/admin/urun/ekle")
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
@router.get("/admin/urunler", response_class=HTMLResponse)
def admin_urunler(request: Request, db: Session = Depends(get_db)):
    urunler = crud.urunleri_listele(db, limit=1000)
    return templates.TemplateResponse("admin_urunler.html", {
        "request": request,
        "urunler": urunler
    })

# ADMİN: Kategoriler
@router.get("/admin/kategoriler", response_class=HTMLResponse)
def admin_kategoriler(request: Request, db: Session = Depends(get_db)):
    kategoriler = crud.kategorileri_listele(db)
    return templates.TemplateResponse("admin_kategoriler.html", {
        "request": request,
        "kategoriler": kategoriler
    })

@router.post("/admin/kategoriler")
def admin_kategori_ekle(
    ad: str = Form(...),
    aciklama: str = Form(""),
    db: Session = Depends(get_db)
):
    kategori_data = schemas.KategoriOlustur(
        ad=ad,
        aciklama=aciklama
    )
    crud.kategori_olustur(db, kategori_data)
    return RedirectResponse(url="/admin/kategoriler", status_code=303)
