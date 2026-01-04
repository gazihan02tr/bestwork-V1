from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, HTMLResponse
from app import models, crud, schemas
from app.dependencies import get_db, templates

router = APIRouter()

# SERTİFİKALAR
@router.get("/sertifikalar", response_class=HTMLResponse)
def sertifikalar_sayfasi(request: Request):
    return templates.TemplateResponse("sertifikalar.html", {
        "request": request
    })

# KURUMSAL
@router.get("/kurumsal", response_class=HTMLResponse)
def kurumsal_sayfasi(request: Request):
    return templates.TemplateResponse("kurumsal.html", {
        "request": request
    })

# --- İLETİŞİM SAYFASI ---
@router.get("/iletisim", response_class=HTMLResponse)
async def iletisim_sayfasi(request: Request):
    return templates.TemplateResponse("iletisim.html", {"request": request})

@router.post("/iletisim", response_class=HTMLResponse)
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
@router.get("/varis-islemleri", response_class=HTMLResponse)
async def varis_islemleri_sayfasi(request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=302)
    
    varisler = crud.varisleri_getir(db, request.state.user.id)
    return templates.TemplateResponse("varis_islemleri.html", {"request": request, "varis_members": varisler, "user": request.state.user})

@router.post("/varis-kaydet")
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

@router.post("/varis-sil")
async def delete_varis(
    request: Request,
    entry_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if not request.state.user:
        return RedirectResponse(url="/giris", status_code=302)
        
    crud.varis_sil(db, entry_id, request.state.user.id)
    return RedirectResponse(url="/varis-islemleri", status_code=302)
