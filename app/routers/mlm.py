from fastapi import APIRouter, Depends, Request, HTTPException, Form
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse
from app import models, crud
from app.dependencies import get_db, templates

router = APIRouter()

@router.get("/api/tree/{user_id}")
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

@router.get("/api/bekleyen-uyeler/{user_id}")
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

@router.post("/api/yerlestir")
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

@router.get("/panel/agac/{user_id}", response_class=HTMLResponse)
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
