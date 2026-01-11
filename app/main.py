from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
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

# --- EXCEPTION HANDLERS ---
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# --- MIDDLEWARE: KULLANICI BİLGİSİNİ YÜKLE ---
@app.middleware("http")
async def add_context_to_request(request: Request, call_next):
    # JWT TOKEN KONTROLÜ
    token = request.cookies.get("access_token")
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

        # 2. Kullanıcı Bilgileri (JWT Çözümleme)
        user_id = None
        
        # Debug Log
        if token:
             print(f"Token bulundu: {token[:10]}...") 
        else:
             pass # Token yok
             
        if token and token.startswith("Bearer "):
            from app import utils # Circular import önlemek için burada
            scheme, _, param = token.partition(" ")
            payload = utils.decode_access_token(param)
            if payload:
                user_id = int(payload.get("sub"))
                print(f"Token decode edildi: User ID {user_id}")
            else:
                print("Token decode edilemedi veya süresi dolmuş.")
        
        # Fallback: Eski user_id cookie varsa (geçici destek, production'da kaldırın)
        if not user_id and request.cookies.get("user_id"):
             # Güvensiz yöntemi devre dışı bıraktık.
             pass

        if user_id:
            user = db.query(models.Kullanici).filter(models.Kullanici.id == user_id).first()
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
    
    # --- ADMIN GÜVENLİK DUVARI (Middleware) ---
    # /admin ile başlayan tüm sayfalara erişim kontrolü
    if request.url.path.startswith("/admin"):
        admin_token = request.cookies.get("admin_token")
        is_authenticated = False
        
        if admin_token and admin_token.startswith("Bearer "):
            from app import utils
            # Basit decode işlemi
            _, _, token_str = admin_token.partition(" ")
            payload = utils.decode_access_token(token_str)
            if payload and str(payload.get("sub", "")).startswith("admin:"):
                is_authenticated = True
                request.state.admin_user = payload.get("sub").split(":")[1]
        
        if not is_authenticated:
            return RedirectResponse(url="/bestsoft", status_code=303)
    
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
