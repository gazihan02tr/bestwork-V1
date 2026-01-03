#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BestWork Web Installer - Tek Dosya Sürümü
Modern, responsive ve otomatik tarayıcı açan kurulum sihirbazı
FastAPI + Uvicorn + WebSocket + Embedded HTML
"""

import os
import sys
import json
import getpass
import asyncio
import webbrowser
import threading
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import create_engine, text
import uvicorn

# Proje dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="BestWork Installer", version="1.0.0")

# WebSocket bağlantı yönetimi
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Global installation state
installation_state = {
    'status': 'idle',
    'progress': 0,
    'current_step': '',
    'logs': [],
    'db_config': None
}

async def log_message(message: str, type: str = "info"):
    """Log mesajı ekle ve WebSocket üzerinden gönder"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'type': type
    }
    installation_state['logs'].append(log_entry)
    
    await manager.send_message({
        'type': 'log',
        'data': log_entry
    })

async def update_progress(progress: int, step: str = ""):
    """İlerleme durumunu güncelle"""
    installation_state['progress'] = progress
    if step:
        installation_state['current_step'] = step
    
    await manager.send_message({
        'type': 'progress',
        'data': {
            'progress': progress,
            'step': step
        }
    })

# HTML Template (Gömülü)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BestSoft Kurulum Ekranı</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f5f5f5; /* MD3 Surface Container Low */
        }
        .md3-card {
            background-color: #ffffff; /* MD3 Surface */
            border-radius: 24px; /* MD3 Large Shape */
            box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.30); /* MD3 Elevation 1 */
        }
        .md3-filled-btn {
            background-color: #6750A4; /* MD3 Primary */
            color: #ffffff; /* MD3 On Primary */
            border-radius: 100px; /* MD3 Full Shape */
            padding: 10px 24px;
            font-weight: 500;
            transition: box-shadow 0.2s, background-color 0.2s;
        }
        .md3-filled-btn:hover {
            background-color: #6750A4;
            box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15); /* Elevation 2 */
        }
        .md3-filled-btn:disabled {
            background-color: #1D1B201F; /* On Surface 12% */
            color: #1D1B2061; /* On Surface 38% */
            box-shadow: none;
            cursor: not-allowed;
        }
        .md3-text-field {
            background-color: #f0f0f0; /* Surface Container Highest */
            border-radius: 4px 4px 0 0;
            border-bottom: 1px solid #49454F; /* Outline */
            transition: background-color 0.2s;
        }
        .md3-text-field:focus-within {
            border-bottom: 2px solid #6750A4; /* Primary */
            background-color: #e6e6e6;
        }
        .md3-text-field input {
            background: transparent;
            border: none;
            outline: none;
            width: 100%;
            padding: 24px 16px 8px 16px;
            font-size: 16px;
            color: #1D1B20; /* On Surface */
        }
        .md3-text-field label {
            position: absolute;
            left: 16px;
            top: 18px;
            font-size: 16px;
            color: #49454F; /* On Surface Variant */
            transition: 0.2s ease all;
            pointer-events: none;
        }
        .md3-text-field input:focus ~ label,
        .md3-text-field input:not(:placeholder-shown) ~ label {
            top: 6px;
            font-size: 12px;
            color: #6750A4; /* Primary */
        }
        .terminal-log {
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: monospace;
        }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">

    <div class="md3-card w-full max-w-4xl p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
        
        <!-- Sol Taraf: Başlık ve Form -->
        <div class="space-y-6">
            <div>
                <h1 class="text-3xl font-normal text-[#1D1B20]">BestSoft</h1>
                <p class="text-[#49454F] text-lg">Kurulum Ekranı</p>
            </div>

            <form id="dbForm" class="space-y-4">
                <div class="md3-text-field relative">
                    <input type="text" id="host" value="{{ current_config['host'] }}" placeholder=" " required>
                    <label for="host">Sunucu (Host)</label>
                </div>
                
                <div class="md3-text-field relative">
                    <input type="text" id="port" value="{{ current_config['port'] }}" placeholder=" " required>
                    <label for="port">Port</label>
                </div>
                
                <div class="md3-text-field relative">
                    <input type="text" id="dbname" value="{{ current_config['dbname'] }}" placeholder=" " required>
                    <label for="dbname">Veritabanı Adı</label>
                </div>
                
                <div class="md3-text-field relative">
                    <input type="text" id="user" value="{{ current_config['user'] }}" placeholder=" " required>
                    <label for="user">Kullanıcı Adı</label>
                </div>
                
                <div class="md3-text-field relative">
                    <input type="password" id="password" value="{{ current_config['password'] }}" placeholder=" ">
                    <label for="password">Şifre</label>
                </div>

                <div class="flex gap-4 pt-2">
                    <button type="button" onclick="testConnection()" id="testBtn" class="md3-filled-btn flex-1 flex items-center justify-center gap-2">
                        <span class="material-symbols-outlined text-lg">link</span>
                        Bağlantıyı Test Et
                    </button>
                </div>
                <div id="connectionStatus" class="hidden text-sm mt-2"></div>
            </form>
        </div>

        <!-- Sağ Taraf: İşlem ve Loglar -->
        <div class="flex flex-col space-y-6">
            
            <div class="bg-[#F3EDF7] p-6 rounded-2xl space-y-4">
                <h2 class="text-xl text-[#1D1B20] font-medium">Sistem Kurulumu</h2>
                <p class="text-[#49454F] text-sm">Veritabanı tabloları oluşturulacak ve örnek veriler yüklenecektir.</p>
                
                <button type="button" onclick="startInstallation()" id="installBtn" disabled class="md3-filled-btn w-full flex items-center justify-center gap-2 bg-[#2E7D32] hover:bg-[#1B5E20]">
                    <span class="material-symbols-outlined text-lg">rocket_launch</span>
                    Kurulumu Başlat
                </button>

                <!-- Progress Bar -->
                <div id="progressContainer" class="hidden space-y-1">
                    <div class="flex justify-between text-xs text-[#49454F]">
                        <span id="progressText">Hazırlanıyor...</span>
                        <span id="progressPercent">0%</span>
                    </div>
                    <div class="w-full bg-[#E0E0E0] rounded-full h-1">
                        <div id="progressBar" class="bg-[#6750A4] h-1 rounded-full transition-all duration-300" style="width: 0%"></div>
                    </div>
                </div>
            </div>

            <div class="flex-1 flex flex-col">
                <h3 class="text-sm font-medium text-[#49454F] mb-2">Sistem Logları</h3>
                <div id="logContainer" class="terminal-log flex-1 rounded-xl p-4 text-xs overflow-y-auto h-48 custom-scrollbar">
                    <div class="text-gray-400">> BestSoft Kurulum Sihirbazı hazır.</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let connectionTested = false;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'log') addLog(data.data);
                else if (data.type === 'progress') updateProgress(data.data.progress, data.data.step);
            };
            
            ws.onclose = () => setTimeout(connectWebSocket, 3000);
        }
        
        function addLog(logData) {
            const logContainer = document.getElementById('logContainer');
            const logLine = document.createElement('div');
            const time = logData.timestamp;
            
            let colorClass = 'text-gray-300';
            if (logData.type === 'success') colorClass = 'text-green-400';
            else if (logData.type === 'error') colorClass = 'text-red-400';
            else if (logData.type === 'warning') colorClass = 'text-yellow-400';
            
            logLine.className = `${colorClass} mb-1`;
            logLine.innerHTML = `<span class="text-gray-500">[${time}]</span> ${logData.message}`;
            
            logContainer.appendChild(logLine);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        function updateProgress(progress, step) {
            document.getElementById('progressContainer').classList.remove('hidden');
            document.getElementById('progressBar').style.width = progress + '%';
            document.getElementById('progressPercent').textContent = progress + '%';
            document.getElementById('progressText').textContent = step;
        }
        
        async function testConnection() {
            const btn = document.getElementById('testBtn');
            const originalContent = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="material-symbols-outlined animate-spin">refresh</span> Test Ediliyor...';
            
            const data = {
                host: document.getElementById('host').value,
                port: document.getElementById('port').value,
                dbname: document.getElementById('dbname').value,
                user: document.getElementById('user').value,
                password: document.getElementById('password').value
            };
            
            try {
                const response = await fetch('/api/test-connection', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                const statusDiv = document.getElementById('connectionStatus');
                statusDiv.classList.remove('hidden');
                
                if (result.success) {
                    statusDiv.className = 'text-sm mt-2 text-green-600 font-medium flex items-center gap-1';
                    statusDiv.innerHTML = '<span class="material-symbols-outlined text-sm">check_circle</span> Bağlantı Başarılı';
                    connectionTested = true;
                    document.getElementById('installBtn').disabled = false;
                    
                    await fetch('/api/save-config', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                } else {
                    statusDiv.className = 'text-sm mt-2 text-red-600 font-medium flex items-center gap-1';
                    statusDiv.innerHTML = `<span class="material-symbols-outlined text-sm">error</span> ${result.message}`;
                    connectionTested = false;
                    document.getElementById('installBtn').disabled = true;
                }
            } catch (error) {
                console.error(error);
            }
            
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
        
        async function startInstallation() {
            if (!connectionTested) return;
            
            const btn = document.getElementById('installBtn');
            btn.disabled = true;
            
            try {
                await fetch('/api/install', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
            } catch (error) {
                alert('Hata: ' + error.message);
                btn.disabled = false;
            }
        }
        
        window.onload = connectWebSocket;
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Ana sayfa"""
    current_config = load_current_config()
    
    # Template'i render et
    html = HTML_TEMPLATE
    for key, value in current_config.items():
        html = html.replace(f"{{{{ current_config['{key}'] }}}}", str(value))
    
    return HTMLResponse(content=html)

@app.get("/api/config")
async def get_config():
    """Mevcut yapılandırmayı getir"""
    return JSONResponse(load_current_config())

@app.post("/api/test-connection")
async def test_connection(data: dict):
    """Veritabanı bağlantısını test et"""
    try:
        user = data.get('user', '')
        password = data.get('password', '')
        host = data.get('host', 'localhost')
        port = data.get('port', '5432')
        dbname = data.get('dbname', 'bestwork')
        
        if password:
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        else:
            db_url = f"postgresql://{user}@{host}:{port}/{dbname}"
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        installation_state['db_config'] = {
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'dbname': dbname,
            'url': db_url
        }
        
        return JSONResponse({
            'success': True,
            'message': 'Veritabanı bağlantısı başarılı! Kuruluma geçebilirsiniz.'
        })
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'message': f'Bağlantı hatası: {str(e)}'
        }, status_code=400)

@app.post("/api/save-config")
async def save_config(data: dict):
    """Yapılandırmayı .env dosyasına kaydet"""
    try:
        user = data.get('user', '')
        password = data.get('password', '')
        host = data.get('host', 'localhost')
        port = data.get('port', '5432')
        dbname = data.get('dbname', 'bestwork')
        
        if password:
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        else:
            db_url = f"postgresql://{user}@{host}:{port}/{dbname}"
        
        env_content = f"""DATABASE_URL={db_url}
SECRET_KEY=supersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        os.environ["DATABASE_URL"] = db_url
        
        return JSONResponse({
            'success': True,
            'message': 'Yapılandırma .env dosyasına kaydedildi.'
        })
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'message': f'Kayıt hatası: {str(e)}'
        }, status_code=500)

@app.post("/api/install")
async def start_installation():
    """Tam kurulumu başlat"""
    if installation_state['status'] == 'running':
        return JSONResponse({
            'success': False,
            'message': 'Kurulum zaten çalışıyor!'
        }, status_code=400)
    
    if not installation_state['db_config']:
        return JSONResponse({
            'success': False,
            'message': 'Önce veritabanı bağlantısını test edin!'
        }, status_code=400)
    
    threading.Thread(target=run_installation_sync, daemon=True).start()
    
    return JSONResponse({
        'success': True,
        'message': 'Kurulum başlatıldı...'
    })

def run_installation_sync():
    """Kurulum işlemini senkron olarak çalıştır"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_installation())

async def run_installation():
    """Kurulum işlemini çalıştır"""
    installation_state['status'] = 'running'
    installation_state['progress'] = 0
    installation_state['logs'] = []
    
    try:
        await log_message("🚀 Kurulum başlatılıyor...", "info")
        await update_progress(10, "Başlatılıyor...")
        await asyncio.sleep(0.5)
        
        await log_message("🗄️ Veritabanı tabloları oluşturuluyor...", "info")
        await update_progress(20, "Veritabanı tabloları oluşturuluyor...")
        
        from app.database import engine, Base
        from app import models
        
        Base.metadata.create_all(bind=engine)
        await log_message("✅ Tablolar başarıyla oluşturuldu.", "success")
        await update_progress(40, "Tablolar oluşturuldu")
        await asyncio.sleep(0.3)
        
        await log_message("👤 Kök (Admin) kullanıcı kontrol ediliyor...", "info")
        await update_progress(50, "Admin kullanıcı oluşturuluyor...")
        
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            mevcut = db.query(models.Kullanici).first()
            if mevcut:
                await log_message(f"ℹ️ Zaten bir kullanıcı var: {mevcut.tam_ad}", "warning")
            else:
                root = models.Kullanici(
                    tam_ad="BestWork Kurucu",
                    email="admin@bestwork.com",
                    telefon="05550001122",
                    sifre="123456",
                    referans_id=None,
                    parent_id=None,
                    kol=None,
                    uye_no="900000001"
                )
                db.add(root)
                db.commit()
                await log_message(f"✅ Kök Kullanıcı Oluşturuldu: {root.tam_ad}", "success")
                await log_message(f"📧 Email: admin@bestwork.com | Şifre: 123456", "info")
        except Exception as e:
            db.rollback()
            raise e
        
        await update_progress(60, "Admin kullanıcı hazır")
        await asyncio.sleep(0.3)
        
        await log_message("📁 Kategoriler ekleniyor...", "info")
        await update_progress(70, "Kategoriler ekleniyor...")
        
        kategoriler = [
            {"ad": "Elektronik", "aciklama": "Teknoloji ürünleri", "resim_url": "💻"},
            {"ad": "Giyim", "aciklama": "Kıyafet ve tekstil", "resim_url": "👔"},
            {"ad": "Kozmetik", "aciklama": "Güzellik ürünleri", "resim_url": "💄"},
            {"ad": "Ev & Yaşam", "aciklama": "Ev eşyaları", "resim_url": "🏠"},
        ]
        
        for kat in kategoriler:
            existing = db.query(models.Kategori).filter(models.Kategori.ad == kat["ad"]).first()
            if not existing:
                db_kat = models.Kategori(**kat)
                db.add(db_kat)
                await log_message(f"  ✓ Kategori eklendi: {kat['ad']}", "success")
        
        db.commit()
        await update_progress(80, "Kategoriler eklendi")
        await asyncio.sleep(0.3)
        
        await log_message("📦 Örnek ürünler ekleniyor...", "info")
        await update_progress(85, "Ürünler ekleniyor...")
        
        urunler = get_sample_products()
        
        added_count = 0
        for urun_data in urunler:
            existing = db.query(models.Urun).filter(models.Urun.ad == urun_data["ad"]).first()
            if not existing:
                db_urun = models.Urun(**urun_data)
                db.add(db_urun)
                added_count += 1
                await log_message(f"  ✓ Ürün eklendi: {urun_data['ad']}", "success")
        
        db.commit()
        db.close()
        
        await update_progress(100, "Kurulum tamamlandı!")
        await log_message(f"✨ {added_count} ürün başarıyla eklendi!", "success")
        await log_message("🎉 BestWork sistemi kullanıma hazır!", "success")
        await log_message("🔐 Giriş Bilgileri: admin@bestwork.com / 123456", "info")
        
        installation_state['status'] = 'completed'
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        await log_message(f"❌ HATA: {str(e)}", "error")
        await log_message(f"Detay: {error_msg}", "error")
        installation_state['status'] = 'error'
        await update_progress(0, "Hata oluştu")

def get_sample_products():
    """Örnek ürün listesi"""
    return [
        {
            "ad": "Akıllı Telefon",
            "aciklama": "En son teknoloji ile donatılmış, yüksek performanslı akıllı telefon. 5G destekli, 128GB hafıza.",
            "fiyat": 12999.00,
            "indirimli_fiyat": 9999.00,
            "stok": 50,
            "kategori_id": 1,
            "resim_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
            "pv_degeri": 500
        },
        {
            "ad": "Kablosuz Kulaklık",
            "aciklama": "Aktif gürültü engelleme özellikli, 30 saat pil ömrü sunan premium kulaklık.",
            "fiyat": 2499.00,
            "indirimli_fiyat": 1999.00,
            "stok": 100,
            "kategori_id": 1,
            "resim_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            "pv_degeri": 100
        },
        {
            "ad": "Erkek Gömlek",
            "aciklama": "Pamuklu, şık ve rahat kesim erkek gömleği. Günlük ve iş hayatınız için ideal.",
            "fiyat": 599.00,
            "stok": 75,
            "kategori_id": 2,
            "resim_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400",
            "pv_degeri": 30
        },
        {
            "ad": "Kadın Elbise",
            "aciklama": "Modern ve zarif tasarım, özel günler için mükemmel bir seçim.",
            "fiyat": 899.00,
            "indirimli_fiyat": 699.00,
            "stok": 40,
            "kategori_id": 2,
            "resim_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
            "pv_degeri": 40
        },
        {
            "ad": "Nemlendirici Krem",
            "aciklama": "Doğal içerikli, tüm cilt tiplerine uygun nemlendirici. 24 saat etki.",
            "fiyat": 349.00,
            "indirimli_fiyat": 249.00,
            "stok": 200,
            "kategori_id": 3,
            "resim_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400",
            "pv_degeri": 20
        },
        {
            "ad": "Makyaj Seti",
            "aciklama": "Profesyonel makyaj seti, 12 parça. Her duruma uygun renkler.",
            "fiyat": 1299.00,
            "indirimli_fiyat": 999.00,
            "stok": 60,
            "kategori_id": 3,
            "resim_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400",
            "pv_degeri": 80
        },
        {
            "ad": "Kahve Makinesi",
            "aciklama": "Otomatik kahve makinesi, 15 bar basınç, süt köpürtme özelliği.",
            "fiyat": 3499.00,
            "indirimli_fiyat": 2799.00,
            "stok": 30,
            "kategori_id": 4,
            "resim_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400",
            "pv_degeri": 150
        },
        {
            "ad": "Yastık Seti",
            "aciklama": "Anti-alerjik, ortopedik yastık seti. 2 adet, farklı sertlik seçenekleri.",
            "fiyat": 799.00,
            "indirimli_fiyat": 599.00,
            "stok": 120,
            "kategori_id": 4,
            "resim_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400",
            "pv_degeri": 35
        },
    ]

def load_current_config():
    """Mevcut .env yapılandırmasını yükle"""
    config = {
        'host': 'localhost',
        'port': '5432',
        'dbname': 'bestwork',
        'user': getpass.getuser(),
        'password': ''
    }
    
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("DATABASE_URL="):
                        url = line.split("=", 1)[1].strip()
                        if "://" in url:
                            prefix, rest = url.split("://", 1)
                            if "@" in rest:
                                creds, addr_db = rest.split("@", 1)
                                user_pass = creds.split(":", 1)
                                config['user'] = user_pass[0]
                                config['password'] = user_pass[1] if len(user_pass) > 1 else ""
                                
                                if "/" in addr_db:
                                    addr, dbname = addr_db.split("/", 1)
                                    host_port = addr.split(":", 1)
                                    config['host'] = host_port[0]
                                    config['port'] = host_port[1] if len(host_port) > 1 else "5432"
                                    config['dbname'] = dbname
        except:
            pass
    
    return config

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket bağlantısı"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def open_browser():
    """Tarayıcıyı otomatik aç"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:8765')

if __name__ == "__main__":
    print("=" * 80)
    print("🚀  BESTWORK KURULUM SİHİRBAZI")
    print("=" * 80)
    print("📡  Sunucu Adresi : http://localhost:8765")
    print("🌐  Tarayıcı     : Otomatik açılacak...")
    print("⚡  WebSocket    : Gerçek zamanlı log aktarımı aktif")
    print("=" * 80)
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8765,
        log_level="warning"
    )