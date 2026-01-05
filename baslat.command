#!/bin/bash

# Terminal penceresinin kapanmasını önlemek için trap (Hata veya çıkış durumunda bekler)
trap 'echo ""; read -p "Kapatmak için Enter tuşuna basın..."' EXIT

# Scriptin çalıştığı dizine git (Çift tıklama ile çalıştırıldığında önemli)
cd "$(dirname "$0")"

echo "================================================"
echo "   BestWork V8 - Otomatik Kurulum ve Başlatma   "
echo "================================================"

# 1. Python Kontrolü
if ! command -v python3 &> /dev/null; then
    echo "HATA: Python 3 sistemde bulunamadı!"
    echo "Lütfen Python 3 yükleyin: https://www.python.org/"
    exit 1
fi

# 2. Sanal Ortam (.venv) Kontrolü ve Oluşturma
if [ ! -d ".venv" ]; then
    echo "-> Sanal ortam (.venv) oluşturuluyor..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "HATA: Sanal ortam oluşturulamadı."
        exit 1
    fi
    echo "-> Sanal ortam başarıyla oluşturuldu."
else
    echo "-> Sanal ortam (.venv) zaten mevcut."
fi

# 3. Sanal Ortamı Aktifleştirme
echo "-> Sanal ortam aktifleştiriliyor..."
source .venv/bin/activate

# 4. Pip Güncelleme (Opsiyonel ama önerilir)
echo "-> Pip güncelleniyor..."
pip install --upgrade pip &> /dev/null

# 5. Bağımlılıkların Yüklenmesi
if [ -f "requirements.txt" ]; then
    echo "-> Gerekli kütüphaneler kontrol ediliyor ve yükleniyor..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "HATA: Kütüphaneler yüklenirken bir sorun oluştu."
        exit 1
    fi
else
    echo "UYARI: requirements.txt dosyası bulunamadı!"
fi

# 6. Uygulamayı Başlatma (Installer Wizard)
echo "================================================"
echo "   Uygulama Başlatılıyor: installer_wizard.py   "
echo "================================================"

python installer_wizard.py
