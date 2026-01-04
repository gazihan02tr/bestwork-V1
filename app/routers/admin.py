from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, HTMLResponse
from app import models, crud, schemas
from app.dependencies import get_db, templates

router = APIRouter()

# ADMIN KONTROL SAYFASI
@router.get("/admin/kontrol", response_class=HTMLResponse)
def admin_ayar_sayfasi(request: Request, db: Session = Depends(get_db)):
    # Admin kontrolü yapılmalı (şimdilik basit kontrol)
    # if not request.state.user or not request.state.user.is_admin:
    #     return RedirectResponse(url="/giris", status_code=303)
    
    nesiller = db.query(models.Nesil).order_by(models.Nesil.derinlik).all()
    site_ayarlari = db.query(models.SiteAyarlari).first()
    
    return templates.TemplateResponse("admin_ayarlar.html", {
        "request": request,
        "nesiller": nesiller,
        "ayarlar": site_ayarlari
    })

# --- ADMIN İŞLEMLERİ ---
@router.post("/admin/ayarlar/guncelle")
def admin_ayarlari_guncelle(
    request: Request,
    site_name: str = Form(...),
    min_cekime_limiti: float = Form(...),
    db: Session = Depends(get_db)
):
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
    
    ayarlar.site_basligi = site_name
    ayarlar.min_cekime_limiti = min_cekime_limiti
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
