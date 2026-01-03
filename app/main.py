from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas, crud
from .database import SessionLocal, engine

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

# Rütbe Gereksinimleri
RUTBE_GEREKSINIMLERI = [
    {"ad": "Distribütör", "sol_pv": 0, "sag_pv": 0},
    {"ad": "Platinum", "sol_pv": 5000, "sag_pv": 5000},
    {"ad": "Pearl", "sol_pv": 15000, "sag_pv": 15000},
    {"ad": "Sapphire", "sol_pv": 50000, "sag_pv": 50000},
    {"ad": "Ruby", "sol_pv": 100000, "sag_pv": 100000},
    {"ad": "Emerald", "sol_pv": 250000, "sag_pv": 250000},
    {"ad": "Diamond", "sol_pv": 500000, "sag_pv": 500000},
    {"ad": "Double Diamond", "sol_pv": 1000000, "sag_pv": 1000000},
    {"ad": "Triple Diamond", "sol_pv": 2500000, "sag_pv": 2500000},
    {"ad": "President", "sol_pv": 5000000, "sag_pv": 5000000},
    {"ad": "Double President", "sol_pv": 10000000, "sag_pv": 10000000},
    {"ad": "Triple President", "sol_pv": 25000000, "sag_pv": 25000000},
]

app = FastAPI(title="BestWork Binary Network Marketing")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def format_large_number(value):
    if value is None:
        return "0"
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
        
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 100_000:
        return f"{num/1_000:.0f}K"
    else:
        if num % 1 == 0:
            return str(int(num))
        return f"{num:.2f}"

templates.env.filters["format_large_number"] = format_large_number

# --- MIDDLEWARE: KULLANICI BİLGİSİNİ YÜKLE ---
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    user_id = request.cookies.get("user_id")
    request.state.user = None
    request.state.cart_count = 0
    
    if user_id:
        db = SessionLocal()
        try:
            user = db.query(models.Kullanici).filter(models.Kullanici.id == int(user_id)).first()
            if user:
                request.state.user = user
                
                # Sepet sayısını hesapla
                sepet = db.query(models.Sepet).filter(models.Sepet.kullanici_id == user.id).first()
                if sepet:
                    cart_items = db.query(models.SepetUrun).filter(models.SepetUrun.sepet_id == sepet.id).all()
                    total_items = sum(item.adet for item in cart_items)
                    request.state.cart_count = total_items
        except:
            pass
        finally:
            db.close()
    
    response = await call_next(request)
    return response

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
    bekleyenler = db.query(models.Kullanici).filter(
        models.Kullanici.referans_id == user_id,
        models.Kullanici.parent_id == None
    ).count()

    # Rütbe Mantığı
    rutbeler = [
        "Distribütör", 
        "Platinum", 
        "Pearl", 
        "Sapphire", 
        "Ruby", 
        "Emerald", 
        "Diamond", 
        "Double Diamond", 
        "Triple Diamond", 
        "President", 
        "Double President", 
        "Triple President"
    ]
    mevcut_rutbe = getattr(kullanici, 'rutbe', 'Distribütör')
    
    try:
        mevcut_index = rutbeler.index(mevcut_rutbe)
        sonraki_rutbe = rutbeler[mevcut_index + 1] if mevcut_index + 1 < len(rutbeler) else None
    except ValueError:
        sonraki_rutbe = "Platinum" # Bilinmeyen rütbe ise varsayılan

    return {
        "id": kullanici.id,
        "uye_no": kullanici.uye_no,
        "tam_ad": kullanici.tam_ad,
        "email": kullanici.email,
        "rutbe": mevcut_rutbe,
        "sonraki_rutbe": sonraki_rutbe,
        "toplam_cv": kullanici.toplam_cv,
        "mevcut_sol_pv": kullanici.sol_pv,
        "mevcut_sag_pv": kullanici.sag_pv,
        "toplam_sol_ekip": sol_ekip,
        "toplam_sag_ekip": sag_ekip,
        "referans_sayisi": referanslar,
        "bekleyen_sayisi": bekleyenler
    }

# --- KİMLİK DOĞRULAMA (AUTH) ---

@app.get("/giris", response_class=HTMLResponse)
def giris_sayfasi(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/giris", response_class=HTMLResponse)
def giris_yap(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Email veya Üye No ile giriş kontrolü
    user = db.query(models.Kullanici).filter(
        or_(models.Kullanici.email == email, models.Kullanici.uye_no == email)
    ).first()
    
    # Basit şifre kontrolü (Hashleme yoksa)
    if not user or user.sifre != password:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "hata": "Hatalı kullanıcı adı veya şifre!"
        })
    
    # Başarılı giriş
    response = RedirectResponse(url=f"/panel/{user.id}", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id))
    return response

@app.get("/cikis")
def cikis_yap():
    response = RedirectResponse(url="/giris", status_code=303)
    response.delete_cookie("user_id")
    return response

# --- ŞİFRE DEĞİŞTİRME ---
@app.get("/sifre-degistir", response_class=HTMLResponse)
def sifre_degistir_sayfasi(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/giris", status_code=303)
    return templates.TemplateResponse("sifre_degistir.html", {"request": request})

@app.post("/sifre-degistir", response_class=HTMLResponse)
def sifre_degistir_islem(
    request: Request,
    mevcut_sifre: str = Form(...),
    yeni_sifre: str = Form(...),
    yeni_sifre_tekrar: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/giris", status_code=303)
    
    user = db.query(models.Kullanici).filter(models.Kullanici.id == int(user_id)).first()
    
    if not user or user.sifre != mevcut_sifre:
        return templates.TemplateResponse("sifre_degistir.html", {
            "request": request,
            "hata": "Mevcut şifreniz hatalı!"
        })
    
    if yeni_sifre != yeni_sifre_tekrar:
        return templates.TemplateResponse("sifre_degistir.html", {
            "request": request,
            "hata": "Yeni şifreler uyuşmuyor!"
        })
        
    if len(yeni_sifre) < 6:
        return templates.TemplateResponse("sifre_degistir.html", {
            "request": request,
            "hata": "Yeni şifre en az 6 karakter olmalı!"
        })

    crud.sifre_guncelle(db, user.id, yeni_sifre)
    
    return templates.TemplateResponse("sifre_degistir.html", {
        "request": request,
        "basari": "Şifreniz başarıyla güncellendi."
    })

# --- WEB PANEL ENDPOINTS ---

@app.get("/panel/sponsor-olduklarim", response_class=HTMLResponse)
def sponsor_olduklarim_sayfasi(request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=303)
    
    user_id = request.state.user.id
    sponsor_olunanlar = db.query(models.Kullanici).filter(models.Kullanici.referans_id == user_id).all()
    
    return templates.TemplateResponse("sponsored.html", {
        "request": request,
        "uyeler": sponsor_olunanlar,
        "site_branding": {"site_name": "BestWork", "primary_color": "#7C3AED"}
    })

@app.get("/panel/bekleyenler", response_class=HTMLResponse)
def bekleyenler_sayfasi(request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=303)
    
    user_id = request.state.user.id
    bekleyenler = db.query(models.Kullanici).filter(
        models.Kullanici.referans_id == user_id,
        models.Kullanici.parent_id == None
    ).all()
    
    return templates.TemplateResponse("bekleyenler.html", {
        "request": request,
        "uyeler": bekleyenler,
        "site_branding": {"site_name": "BestWork", "primary_color": "#7C3AED"}
    })

# KULLANICI DASHBOARD (Giydirilmiş Hali)
@app.get("/panel/{user_id}", response_class=HTMLResponse)
def dashboard_sayfasi(request: Request, user_id: int, db: Session = Depends(get_db)):
    # GÜVENLİK KONTROLÜ
    current_user = request.state.user
    if not current_user:
        return RedirectResponse(url="/giris", status_code=303)
    
    # Başkasının paneline girmeyi engelle (Admin hariç - şimdilik admin yok)
    if current_user.id != user_id:
        return RedirectResponse(url=f"/panel/{current_user.id}", status_code=303)

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

@app.get("/career-tracking", response_class=HTMLResponse)
def career_tracking_page(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user:
        return RedirectResponse(url="/giris")
    
    current_sol = user.toplam_sol_pv
    current_sag = user.toplam_sag_pv
    
    kariyer_durumu = []
    
    for rutbe in RUTBE_GEREKSINIMLERI:
        hedef_sol = rutbe["sol_pv"]
        hedef_sag = rutbe["sag_pv"]
        
        sol_yuzde = 100
        sag_yuzde = 100
        
        if hedef_sol > 0:
            sol_yuzde = min(100, int((current_sol / hedef_sol) * 100))
        
        if hedef_sag > 0:
            sag_yuzde = min(100, int((current_sag / hedef_sag) * 100))
            
        tamamlandi = (sol_yuzde == 100 and sag_yuzde == 100)
        
        kariyer_durumu.append({
            "ad": rutbe["ad"],
            "hedef_sol": hedef_sol,
            "hedef_sag": hedef_sag,
            "mevcut_sol": min(current_sol, hedef_sol) if hedef_sol > 0 else current_sol,
            "mevcut_sag": min(current_sag, hedef_sag) if hedef_sag > 0 else current_sag,
            "sol_yuzde": sol_yuzde,
            "sag_yuzde": sag_yuzde,
            "tamamlandi": tamamlandi,
            "aktif": user.rutbe == rutbe["ad"]
        })
        
    return templates.TemplateResponse("career_tracking.html", {
        "request": request,
        "kariyer_durumu": kariyer_durumu,
        "current_user": user,
        "site_branding": {"site_name": "BestWork", "primary_color": "#7C3AED"},
        "format_number": lambda x: "{:,}".format(int(x)).replace(",", ".")
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

# --- KAYIT İŞLEMLERİ ---

@app.get("/kayit", response_class=HTMLResponse)
def kayit_sponsor_kontrol(request: Request, ref: str = None):
    if ref:
        return RedirectResponse(url=f"/kayit-form?ref={ref}", status_code=303)
    return templates.TemplateResponse("sponsor_kontrol.html", {"request": request})

@app.get("/api/sponsor-kontrol/{sponsor_no}")
def sponsor_kontrol_api(sponsor_no: str, db: Session = Depends(get_db)):
    # Hem ID hem de uye_no ile arama yapalım
    sponsor = None
    # Eğer sadece sayı ise ID olma ihtimali de var, ama uye_no string de olabilir.
    # Güvenli olması için her ikisine de bakalım.
    sponsor = db.query(models.Kullanici).filter(
        or_(models.Kullanici.uye_no == sponsor_no, models.Kullanici.id == (int(sponsor_no) if sponsor_no.isdigit() else -1))
    ).first()
    
    if sponsor:
        return {"valid": True, "ad_soyad": sponsor.tam_ad, "id": sponsor.id}
    else:
        return {"valid": False}

@app.get("/kayit-form", response_class=HTMLResponse)
def kayit_formu_sayfasi(request: Request, ref: str = None, db: Session = Depends(get_db)):
    sponsor = None
    
    if ref:
        # Referans kodu verilmişse onu bul
        sponsor = db.query(models.Kullanici).filter(
            or_(models.Kullanici.uye_no == ref, models.Kullanici.id == (int(ref) if ref.isdigit() else -1))
        ).first()
    
    if not sponsor:
        # Referans yoksa veya bulunamadıysa, Şirket Kurucusu (ID: 1) veya ilk kullanıcıyı ata
        sponsor = db.query(models.Kullanici).order_by(models.Kullanici.id.asc()).first()
        
    if not sponsor:
        # Hiç kullanıcı yoksa (ilk kurulum), bu durum normalde olmamalı ama handle edelim
        return HTMLResponse("Sistemde hiç üye yok, lütfen önce kurulum yapın.", status_code=500)

    return templates.TemplateResponse("kayit_form.html", {
        "request": request,
        "sponsor": sponsor
    })

@app.post("/kayit-tamamla", response_class=HTMLResponse)
def kayit_tamamla_form(
    request: Request,
    referans_id: int = Form(...),
    ad: str = Form(...),
    soyad: str = Form(...),
    email: str = Form(...),
    telefon: str = Form(...),
    sifre: str = Form(...),
    sifre_tekrar: str = Form(...),
    uyelik_turu: str = Form("Bireysel"),
    ulke: str = Form("Türkiye"),
    dogum_tarihi: str = Form(None),
    cinsiyet: str = Form("KADIN"),
    il: str = Form(None),
    ilce: str = Form(None),
    mahalle: str = Form(None),
    tc_no: str = Form(None),
    vergi_dairesi: str = Form(None),
    vergi_no: str = Form(None),
    posta_kodu: str = Form(None),
    adres: str = Form(None),
    db: Session = Depends(get_db)
):
    if sifre != sifre_tekrar:
        return HTMLResponse("Şifreler uyuşmuyor! <a href='javascript:history.back()'>Geri Dön</a>", status_code=400)
    
    # KullaniciKayit şemasına uygun veri hazırla
    yeni_uye_data = schemas.KullaniciKayit(
        tam_ad=f"{ad} {soyad}",
        email=email,
        telefon=telefon,
        sifre=sifre,
        referans_id=referans_id,
        # Opsiyonel alanlar
        tc_no=tc_no,
        dogum_tarihi=dogum_tarihi,
        cinsiyet=cinsiyet,
        uyelik_turu=uyelik_turu,
        ulke=ulke,
        il=il,
        ilce=ilce,
        mahalle=mahalle,
        adres=adres,
        posta_kodu=posta_kodu,
        vergi_dairesi=vergi_dairesi,
        vergi_no=vergi_no
    )
    
    try:
        yeni_uye = crud.yeni_uye_kaydet(db, yeni_uye_data)
        # Başarılı kayıt sonrası giriş sayfasına yönlendir
        return templates.TemplateResponse("login.html", {
            "request": request,
            "basari": "Kaydınız başarıyla oluşturuldu! Giriş yapabilirsiniz."
        })
    except Exception as e:
        return HTMLResponse(f"Kayıt hatası: {str(e)} <a href='javascript:history.back()'>Geri Dön</a>", status_code=500)

@app.post("/kayit/", response_model=schemas.KullaniciCevap)
def uye_kaydet_api(kullanici: schemas.KullaniciKayit, db: Session = Depends(get_db)):
    return crud.yeni_uye_kaydet(db=db, kullanici_verisi=kullanici)

@app.get("/api/dashboard/{user_id}")
def api_dashboard_getir(user_id: int, db: Session = Depends(get_db)):
    return get_dashboard_data(user_id, db)

# app/main.py içine ekle

@app.get("/api/tree/{user_id}")
def get_tree_data(user_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        raise HTTPException(status_code=401, detail="Giriş yapmalısınız")
    
    if request.state.user.id != user_id:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim")

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
            "uye_no": user.uye_no,
            "pv": f"Sol: {user.sol_pv} | Sağ: {user.sag_pv}",
            "children": [
                build_node(sol_uye.id) if sol_uye else {"name": "Boş", "id": None, "kol": "SOL", "parent": u_id},
                build_node(sag_uye.id) if sag_uye else {"name": "Boş", "id": None, "kol": "SAG", "parent": u_id}
            ]
        }
    
    return build_node(user_id)

@app.get("/api/bekleyen-uyeler/{user_id}")
def get_bekleyen_uyeler(user_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.state.user or request.state.user.id != user_id:
        raise HTTPException(status_code=401, detail="Yetkisiz işlem")

    # Kullanıcının referans olduğu ve henüz ağaca yerleşmemiş (parent_id=None) üyeleri getir
    bekleyenler = db.query(models.Kullanici).filter(
        models.Kullanici.referans_id == user_id,
        models.Kullanici.parent_id == None
    ).all()
    
    return [
        {
            "id": u.id, 
            "uye_no": u.uye_no, 
            "tam_ad": u.tam_ad, 
            "email": u.email,
            "telefon": u.telefon,
            "rutbe": u.rutbe,
            "kayit_tarihi": u.kayit_tarihi.strftime("%d.%m.%Y %H:%M") if u.kayit_tarihi else "-"
        } 
        for u in bekleyenler
    ]

@app.post("/api/yerlestir")
def yerlestir_api(
    request: Request,
    uye_id: int = Form(...),
    parent_id: int = Form(...),
    kol: str = Form(...),
    db: Session = Depends(get_db)
):
    if not request.state.user:
        return JSONResponse(status_code=401, content={"success": False, "message": "Giriş yapmalısınız"})

    # Güvenlik: Sadece sponsoru olduğu üyeyi yerleştirebilir
    uye = db.query(models.Kullanici).filter(models.Kullanici.id == uye_id).first()
    if not uye:
        return JSONResponse(status_code=404, content={"success": False, "message": "Üye bulunamadı"})
    
    if uye.referans_id != request.state.user.id:
        return JSONResponse(status_code=403, content={"success": False, "message": "Bu üyeyi yerleştirme yetkiniz yok!"})

    try:
        crud.uyeyi_agaca_yerlestir(db, uye_id, parent_id, kol)
        return {"success": True, "message": "Üye başarıyla yerleştirildi."}
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"success": False, "message": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})

@app.get("/panel/agac/{user_id}", response_class=HTMLResponse)
def tree_page(request: Request, user_id: int, db: Session = Depends(get_db)):
    # GÜVENLİK KONTROLÜ
    current_user = request.state.user
    if not current_user:
        return RedirectResponse(url="/giris", status_code=303)
    
    # Başkasının ağacını görüntülemeyi engelle (Şimdilik sadece kendi ağacı)
    if current_user.id != user_id:
        return RedirectResponse(url=f"/panel/agac/{current_user.id}", status_code=303)

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
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=303)
    if request.state.user.id != kullanici_id:
        return RedirectResponse(url=f"/sepet/{request.state.user.id}", status_code=303)

    sepet = crud.sepet_detayi_getir(db, kullanici_id)
    return templates.TemplateResponse("sepet.html", {
        "request": request,
        "sepet": sepet,
        "kullanici_id": kullanici_id
    })

# API: Sepete Ürün Ekle
@app.post("/api/sepet/{kullanici_id}/ekle")
def sepete_ekle_api(request: Request, kullanici_id: int, urun_id: int = Form(...), adet: int = Form(1), db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=303)
    
    # Başkasının sepetine eklemeyi engelle -> Kendi sepetine yönlendir
    if request.state.user.id != kullanici_id:
        # Burada kullanıcı ID'sini düzeltip işlemi yapabiliriz ama güvenlik için reddetmek veya yönlendirmek daha iyi.
        # Yönlendirme yaparsak POST verisi kaybolur. O yüzden işlem yapıp kendi sepetine yönlendirelim.
        crud.sepete_urun_ekle(db, request.state.user.id, urun_id, adet)
        return RedirectResponse(url=f"/sepet/{request.state.user.id}", status_code=303)

    crud.sepete_urun_ekle(db, kullanici_id, urun_id, adet)
    return RedirectResponse(url=f"/sepet/{kullanici_id}", status_code=303)

# API: Sepetten Ürün Çıkar
@app.get("/api/sepet/{kullanici_id}/cikar/{sepet_urun_id}")
def sepetten_cikar_api(request: Request, kullanici_id: int, sepet_urun_id: int, db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=303)
    if request.state.user.id != kullanici_id:
        return RedirectResponse(url=f"/sepet/{request.state.user.id}", status_code=303)

    crud.sepetten_urun_cikar(db, kullanici_id, sepet_urun_id)
    return RedirectResponse(url=f"/sepet/{kullanici_id}", status_code=303)

# API: Sipariş Oluştur
@app.post("/api/siparis/{kullanici_id}/olustur")
def siparis_olustur_api(request: Request, kullanici_id: int, adres: str = Form(...), db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=303)
    if request.state.user.id != kullanici_id:
        return RedirectResponse(url=f"/sepet/{request.state.user.id}", status_code=303)

    siparis = crud.siparis_olustur(db, kullanici_id, adres)
    return RedirectResponse(url=f"/siparisler/{kullanici_id}", status_code=303)

# SİPARİŞLERİM
@app.get("/siparisler/{kullanici_id}", response_class=HTMLResponse)
def siparisler_sayfasi(request: Request, kullanici_id: int, db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=303)
    if request.state.user.id != kullanici_id:
        return RedirectResponse(url=f"/siparisler/{request.state.user.id}", status_code=303)

    siparisler = crud.kullanici_siparislerini_getir(db, kullanici_id)
    return templates.TemplateResponse("siparisler.html", {
        "request": request,
        "siparisler": siparisler,
        "kullanici_id": kullanici_id
    })

# MAĞAZA (TÜM ÜRÜNLER)
@app.get("/urunler", response_class=HTMLResponse)
def magaza_sayfasi(request: Request, db: Session = Depends(get_db)):
    kategoriler = crud.kategorileri_listele(db)
    urunler = crud.urunleri_listele(db, limit=100)
    
    # Kategori ürün sayılarını hesapla
    for kat in kategoriler:
        kat.urun_sayisi = db.query(models.Urun).filter(models.Urun.kategori_id == kat.id, models.Urun.aktif == True).count()

    return templates.TemplateResponse("magaza.html", {
        "request": request,
        "kategoriler": kategoriler,
        "urunler": urunler
    })

# SERTİFİKALAR
@app.get("/sertifikalar", response_class=HTMLResponse)
def sertifikalar_sayfasi(request: Request):
    return templates.TemplateResponse("sertifikalar.html", {
        "request": request
    })

# KURUMSAL
@app.get("/kurumsal", response_class=HTMLResponse)
def kurumsal_sayfasi(request: Request):
    return templates.TemplateResponse("kurumsal.html", {
        "request": request
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

# --- İLETİŞİM SAYFASI ---
@app.get("/iletisim", response_class=HTMLResponse)
async def iletisim_sayfasi(request: Request):
    return templates.TemplateResponse("iletisim.html", {"request": request})

@app.post("/iletisim", response_class=HTMLResponse)
async def iletisim_formu_gonder(
    request: Request,
    ad_soyad: str = Form(...),
    email: str = Form(...),
    konu: str = Form(...),
    mesaj: str = Form(...),
    db: Session = Depends(get_db)
):
    yeni_mesaj = schemas.IletisimCreate(
        ad_soyad=ad_soyad,
        email=email,
        konu=konu,
        mesaj=mesaj
    )
    kayit = crud.create_iletisim_mesaji(db, yeni_mesaj)
    return templates.TemplateResponse("iletisim.html", {
        "request": request,
        "basari_mesaji": f"Mesajınız başarıyla alındı. Takip Numaranız: {kayit.takip_no}"
    })

# --- VARİS İŞLEMLERİ ---
@app.get("/varis-islemleri", response_class=HTMLResponse)
async def varis_islemleri_sayfasi(request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=302)
    
    varisler = crud.varisleri_getir(db, request.state.user.id)
    return templates.TemplateResponse("varis_islemleri.html", {"request": request, "varis_members": varisler, "user": request.state.user})

@app.post("/varis-kaydet")
async def save_varis(
    request: Request,
    entry_id: str = Form(None),
    name: str = Form(...),
    tc: str = Form(...),
    phone: str = Form(None),
    email: str = Form(None),
    relation: str = Form(None),
    address: str = Form(None),
    db: Session = Depends(get_db)
):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=302)
    
    # Boş stringleri None'a çevir
    phone = phone if phone and phone.strip() else None
    email = email if email and email.strip() else None
    relation = relation if relation and relation.strip() else None
    address = address if address and address.strip() else None
    
    if entry_id and entry_id.strip():
        varis_update = schemas.VarisUpdate(
            ad_soyad=name,
            tc=tc,
            telefon=phone,
            email=email,
            yakinlik=relation,
            adres=address
        )
        crud.varis_guncelle(db, int(entry_id), varis_update, request.state.user.id)
    else:
        varis_create = schemas.VarisCreate(
            ad_soyad=name,
            tc=tc,
            telefon=phone,
            email=email,
            yakinlik=relation,
            adres=address
        )
        crud.varis_olustur(db, varis_create, request.state.user.id)
        
    return RedirectResponse(url="/varis-islemleri", status_code=302)

@app.post("/varis-sil")
async def delete_varis(
    request: Request,
    entry_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=302)
        
    crud.varis_sil(db, entry_id, request.state.user.id)
    return RedirectResponse(url="/varis-islemleri", status_code=302)
