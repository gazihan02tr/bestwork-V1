from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, HTMLResponse
import subprocess
import os
import json
import time
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
    # Admin modelinde ara
    admin = db.query(models.Admin).filter(models.Admin.kullanici_adi == username).first()
    if not admin or admin.sifre != password:
        return templates.TemplateResponse("bestsoft_login.html", {"request": request, "hata": "Geçersiz Kullanıcı Adı veya Şifre"})
    
    # Admin JWT Token
    from app import utils
    access_token = utils.create_access_token(
        data={"sub": f"admin:{username}"}
    )

    response = RedirectResponse(url="/bestsoft/dashboard", status_code=303)
    response.set_cookie(
        key="admin_token", 
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        secure=False
    )
    return response

@router.get("/admin/logout")
def admin_logout():
    response = RedirectResponse(url="/bestsoft", status_code=303)
    response.delete_cookie("admin_token")
    return response

# Dependency veya Yardımcı Fonksiyon
def get_current_admin(request: Request):
    token = request.cookies.get("admin_token")
    if token and token.startswith("Bearer "):
        from app import utils
        _, _, param = token.partition(" ")
        payload = utils.decode_access_token(param)
        if payload:
            sub = payload.get("sub")
            if sub and sub.startswith("admin:"):
                return sub.split(":")[1]
    return None

# BESTSOFT ADMIN DASHBOARD (YENİ ANASAYFA)
@router.get("/bestsoft/dashboard", response_class=HTMLResponse)
def bestsoft_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
    
    return templates.TemplateResponse("bestsoft_dashboard.html", {"request": request})

# Yardımcı Fonksiyon: Güncelleme Kontrolü
def check_for_updates():
    try:
        should_fetch = True
        info_file = "update_check_info.json"
        
        # 8 Saatlik Kontrol (28800 saniye)
        if os.path.exists(info_file):
            try:
                with open(info_file, "r") as f:
                    data = json.load(f)
                    last_check = data.get("last_check", 0)
                    if time.time() - last_check < 28800:
                        should_fetch = False
            except:
                pass
        
        if should_fetch:
            # Git fetch işlemi (timeout ile)
            subprocess.run(["git", "fetch"], check=True, timeout=10, capture_output=True)
            # Zaman damgasını kaydet
            try:
                with open(info_file, "w") as f:
                    json.dump({"last_check": time.time()}, f)
            except:
                pass

        # Status kontrolü
        result = subprocess.run(["git", "status", "-uno"], check=True, capture_output=True, text=True)
        if "Your branch is behind" in result.stdout:
            return True
    except:
        pass
    return False

def get_system_version():
    try:
        readme_path = os.path.join(os.getcwd(), "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                import re
                content = f.read()
                match = re.search(r"### (v\d+(\.\d+)+)", content)
                if match:
                    return match.group(1)
    except:
        pass
    return "v?.?.?"

def get_remote_system_version():
    try:
        # Fetch remote details first if we haven't recently (relies on check_for_updates having run usually, but safe to run)
        # Assuming origin/main is the target. Better to use @{u} if configured.
        result = subprocess.run(["git", "show", "@{u}:README.md"], capture_output=True, text=True)
        if result.returncode == 0:
            import re
            content = result.stdout
            match = re.search(r"### (v\d+(\.\d+)+)", content)
            if match:
                return match.group(1)
    except:
        pass
    return None

# ADMIN AYARLAR SAYFASI
@router.get("/admin/ayarlar")
def admin_ayarlar_page(request: Request, db: Session = Depends(get_db)):
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
        
    update_available = check_for_updates()
    current_version = get_system_version()
    remote_version = None

    return templates.TemplateResponse("admin_ayarlar.html", {
        "request": request, 
        "update_available": update_available,
        "current_version": current_version,
        "remote_version": remote_version
    })


# ADMIN KONTROL SAYFASI (Eski Rota - Yönlendirme)
@router.get("/admin/kontrol")
def admin_ayar_redirect():
    return RedirectResponse(url="/admin/ayarlar", status_code=303)

# ... Diğer rotalar (Ürünler, Kategoriler vb.) buraya eklenebilir ...

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

# --- SEO AYARLARI ---

@router.get("/admin/ayarlar/seo", response_class=HTMLResponse)
def admin_seo_page(request: Request, db: Session = Depends(get_db)):
    # Check admin auth
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
        
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
        db.commit()
        db.refresh(ayarlar)
        
    return templates.TemplateResponse("admin_seo.html", {"request": request, "ayarlar": ayarlar})

@router.post("/admin/ayarlar/seo")
def admin_seo_update(
    request: Request,
    site_basligi: str = Form(...),
    seo_aciklama: str = Form(""),
    seo_anahtar_kelimeler: str = Form(""),
    seo_yazar: str = Form(""),
    db: Session = Depends(get_db)
):
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
        
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
    
    ayarlar.site_basligi = site_basligi
    ayarlar.seo_aciklama = seo_aciklama
    ayarlar.seo_anahtar_kelimeler = seo_anahtar_kelimeler
    ayarlar.seo_yazar = seo_yazar
    
    db.commit()
    
    # Redirect back with success message
    return RedirectResponse(url="/admin/ayarlar/seo?success=true", status_code=303)

# --- GOOGLE ANALYTICS AYARLARI ---

@router.get("/admin/ayarlar/analytics", response_class=HTMLResponse)
def admin_analytics_page(request: Request, db: Session = Depends(get_db)):
    # Check admin auth
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
        
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
        db.commit()
        db.refresh(ayarlar)
        
    return templates.TemplateResponse("admin_analytics.html", {"request": request, "ayarlar": ayarlar})

@router.post("/admin/ayarlar/analytics")
def admin_analytics_update(
    request: Request,
    google_analytics_kodu: str = Form(""),
    db: Session = Depends(get_db)
):
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
        
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
    
    ayarlar.google_analytics_kodu = google_analytics_kodu
    
    db.commit()
    
    return RedirectResponse(url="/admin/ayarlar/analytics?success=true", status_code=303)

# --- FİRMA BİLGİLERİ AYARLARI ---

@router.get("/admin/ayarlar/firma", response_class=HTMLResponse)
def admin_firma_page(request: Request, db: Session = Depends(get_db)):
    # Check admin auth
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
        
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
        db.commit()
        db.refresh(ayarlar)
        
    return templates.TemplateResponse("admin_firma.html", {"request": request, "ayarlar": ayarlar})

@router.post("/admin/ayarlar/firma")
def admin_firma_update(
    request: Request,
    footer_baslik: str = Form(""),
    footer_aciklama: str = Form(""),
    footer_copyright: str = Form(""),
    iletisim_adres: str = Form(""),
    iletisim_email: str = Form(""),
    iletisim_telefon: str = Form(""),
    iletisim_harita: str = Form(""),
    sosyal_facebook: str = Form(""),
    sosyal_twitter: str = Form(""),
    sosyal_instagram: str = Form(""),
    sosyal_linkedin: str = Form(""),
    sosyal_youtube: str = Form(""),
    db: Session = Depends(get_db)
):
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)
        
    ayarlar = db.query(models.SiteAyarlari).first()
    if not ayarlar:
        ayarlar = models.SiteAyarlari()
        db.add(ayarlar)
    
    ayarlar.footer_baslik = footer_baslik
    ayarlar.footer_aciklama = footer_aciklama
    ayarlar.footer_copyright = footer_copyright
    ayarlar.iletisim_adres = iletisim_adres
    ayarlar.iletisim_email = iletisim_email
    ayarlar.iletisim_telefon = iletisim_telefon
    ayarlar.iletisim_harita = iletisim_harita
    ayarlar.sosyal_facebook = sosyal_facebook
    ayarlar.sosyal_twitter = sosyal_twitter
    ayarlar.sosyal_instagram = sosyal_instagram
    ayarlar.sosyal_linkedin = sosyal_linkedin
    ayarlar.sosyal_youtube = sosyal_youtube
    

    db.commit()
    
    # Redirect back with success message
    return RedirectResponse(url="/admin/ayarlar/firma?success=true", status_code=303)


# --- YENİ: RÜTBE YÖNETİMİ ---

@router.get("/admin/ayarlar/rutbeler", response_class=HTMLResponse)
def admin_rutbeler_page(request: Request, db: Session = Depends(get_db)):
    # Admin yetkilendirmesini kontrol et
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)

    # Veritabanından tüm rütbeleri çek
    rutbeler = crud.get_rutbeler(db)

    return templates.TemplateResponse("admin_rutbeler.html", {
        "request": request,
        "rutbeler": rutbeler
    })

@router.post("/admin/ayarlar/rutbeler")
async def admin_rutbeler_update(request: Request, db: Session = Depends(get_db)):
    # Admin yetkilendirmesini kontrol et
    admin_user = get_current_admin(request)
    if not admin_user:
        return RedirectResponse(url="/bestsoft", status_code=303)

    form_data = await request.form()

    # Formdaki tüm alanları döngüye al
    i = 1
    while f"rutbe_id_{i}" in form_data:
        rutbe_id = int(form_data[f"rutbe_id_{i}"])

        # 'Distribütör' rütbesi hariç diğerlerini güncelle
        if f"sol_pv_{i}" in form_data:
            sol_pv = int(form_data[f"sol_pv_{i}"])
            sag_pv = int(form_data[f"sag_pv_{i}"])

            try:
                crud.update_rutbe(db, rutbe_id, sol_pv, sag_pv)
            except HTTPException as e:
                # Hata durumunda formu hata mesajıyla geri gönder (isteğe bağlı)
                rutbeler = crud.get_rutbeler(db)
                return templates.TemplateResponse("admin_rutbeler.html", {
                    "request": request,
                    "rutbeler": rutbeler,
                    "hata": f"ID {rutbe_id} için hata: {e.detail}"
                })

        i += 1

    # Başarılı güncelleme sonrası yönlendirme
    return RedirectResponse(url="/admin/ayarlar/rutbeler?success=true", status_code=303)


# --- SİSTEM GÜNCELLEME ---
@router.get("/admin/ayarlar/guncelleme", response_class=HTMLResponse)
def admin_ayarlar_guncelleme(request: Request):
    # Read the README.md content
    readme_content = ""
    try:
        # Assuming README.md is in the root directory
        readme_path = os.path.join(os.getcwd(), "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_content = f.read()
        else:
            readme_content = "README.md dosyası bulunamadı."
    except Exception as e:
        readme_content = f"README dosyası okunamadı: {str(e)}"
    
    result_message = request.query_params.get("message")
    update_available = check_for_updates()

    return templates.TemplateResponse("admin_ayarlar_guncelleme.html", {
        "request": request,
        "readme_content": readme_content,
        "result_message": result_message,
        "update_available": update_available
    })

@router.post("/admin/ayarlar/guncelleme/check")
def admin_ayarlar_guncelleme_check(request: Request):
    try:
        # Run git fetch
        subprocess.run(["git", "fetch"], check=True, capture_output=True)
        
        # Manuel kontrol yapıldığı için zamanlayıcıyı güncelle
        try:
            info_file = "update_check_info.json"
            with open(info_file, "w") as f:
                json.dump({"last_check": time.time()}, f)
        except:
            pass

        # Check status
        result = subprocess.run(["git", "status", "-uno"], check=True, capture_output=True, text=True)
        raw_output = result.stdout
        
        # Output Parsing & Formatting
        message = ""
        lines = raw_output.splitlines()
        
        # Check Main Status
        if "Your branch is up to date" in raw_output:
            message += "✅ SİSTEM GÜNCEL\n\n"
            message += "Sisteminiz şu anda sunucudaki en son versiyonla senkronizedir.\n"
        elif "Your branch is behind" in raw_output:
            message += "⚠️ GÜNCELLEME MEVCUT\n\n"
            message += "Sunucuda yeni bir sürüm bulundu. Lütfen güncelleme butonunu kullanarak sistemi yükseltin.\n"
        else:
            message += "ℹ️ DURUM BİLGİSİ\n\n"
            message += "Git durumu aşağıdadır:\n"

        # Check Local Changes (Dirty State)
        if "Changes not staged for commit" in raw_output or "Changes to be committed" in raw_output:
             message += "\n----------------------------------------\n"
             message += "⚠️ YEREL DEĞİŞİKLİKLER UYARISI:\n"
             message += "Sistemde yerel olarak değiştirilmiş dosyalar var.\n"
             
             # Filter out massive lists of files (like .venv clutter)
             change_lines = [line for line in lines if "modified:" in line or "deleted:" in line or "renamed:" in line]
             if len(change_lines) > 10:
                 message += f"{len(change_lines)} adet dosya farklı görünüyor. (Detaylar gizlendi)\n"
             else:
                 message += "Etkilenen Dosyalar:\n"
                 for line in change_lines:
                     message += f"{line.strip()}\n"

    except Exception as e:
        message = f"Hata oluştu: {str(e)}"
    
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    
    return RedirectResponse(url=f"/admin/ayarlar/guncelleme?message={encoded_message}", status_code=303)

@router.post("/admin/ayarlar/guncelleme/pull")
def admin_ayarlar_guncelleme_pull(request: Request):
    try:
        # Run git pull
        result = subprocess.run(["git", "pull"], check=True, capture_output=True, text=True)
        message = f"Güncelleme Çıktısı:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        # Decode bytes if necessary
        err_msg = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e.stderr)
        message = f"Güncelleme Hatası (Git):\n{err_msg}"
    except Exception as e:
        message = f"Hata: {str(e)}"
    
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    
    return RedirectResponse(url=f"/admin/ayarlar/guncelleme?message={encoded_message}", status_code=303)

