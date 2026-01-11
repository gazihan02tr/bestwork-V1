#!/bin/bash
cd "$(dirname "$0")"

# Renkler
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}BestSoft Launcher (Mac OS)${NC}"

# 1. Sanal Ortam Kontrolü ve Oluşturma
if [ ! -d ".venv" ]; then
    echo "Sanal ortam bulunamadı. Oluşturuluyor..."
    python3 -m venv .venv
    echo -e "${CYAN}Sanal ortam oluşturuldu.${NC}"
fi

# 2. Sanal Ortamı Aktif Et
source .venv/bin/activate

# 3. Pip Güncelleme (Opsiyonel ama iyi olur)
# python -m pip install --upgrade pip > /dev/null 2>&1

# 4. CLI Yöneticisini Başlat
python setup_cli.py

# Çıkışta bekle (Hata olursa okuyabilmek için)
echo -e "${CYAN}Oturum sonlandı.${NC}"
read -p "Kapatmak için Enter'a basın..."
