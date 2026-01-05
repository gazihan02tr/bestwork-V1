from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from . import models
from .database import SessionLocal, engine
from .routers import auth, mlm, shop, general, admin, dashboard

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

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
async def add_context_to_request(request: Request, call_next):
    user_id = request.cookies.get("user_id")
    request.state.user = None
    request.state.cart_count = 0
    request.state.site_ayarlar = None
    
    db = SessionLocal()
    try:
        # 1. Site Ayarlarını Yükle
        site_ayarlar = db.query(models.SiteAyarlari).first()
        if not site_ayarlar:
            site_ayarlar = models.SiteAyarlari() # Varsayılan
        request.state.site_ayarlar = site_ayarlar

        # 2. Kullanıcı Bilgileri
        if user_id:
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

# Router'ları dahil et
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(mlm.router)
app.include_router(shop.router)
app.include_router(general.router)
app.include_router(admin.router)
