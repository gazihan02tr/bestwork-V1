from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, HTMLResponse
from app import models, crud, utils
from app.dependencies import get_db, templates

router = APIRouter()

@router.get("/panel/{user_id}", response_class=HTMLResponse)
def dashboard_sayfasi(request: Request, user_id: int, db: Session = Depends(get_db)):
    # GÜVENLİK KONTROLÜ
    current_user = request.state.user
    if not current_user:
        return RedirectResponse(url="/giris", status_code=303)
    
    # Başkasının paneline girmeyi engelle (Admin hariç - şimdilik admin yok)
    if current_user.id != user_id:
        return RedirectResponse(url=f"/panel/{current_user.id}", status_code=303)

    ozet_verisi = crud.get_dashboard_data(user_id, db)
    
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

@router.get("/api/dashboard/{user_id}")
def api_dashboard_getir(user_id: int, db: Session = Depends(get_db)):
    return crud.get_dashboard_data(user_id, db)

@router.get("/bekleyenler", response_class=HTMLResponse)
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

@router.get("/career-tracking", response_class=HTMLResponse)
def career_tracking_page(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user:
        return RedirectResponse(url="/giris")
    
    current_sol = user.toplam_sol_pv
    current_sag = user.toplam_sag_pv
    
    kariyer_durumu = []
    
    for rutbe in utils.RUTBE_GEREKSINIMLERI:
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
