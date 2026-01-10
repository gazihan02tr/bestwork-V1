#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import platform
import socket

# Renk Kodları
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_banner():
    banner = f"""{BLUE}
    ===============================================
       BESTWORK NETWORK MARKETING - KURULUM SİHİRBAZI
    ===============================================
    v10.1 - Installer Wizard (Redis Integrated)
    {RESET}"""
    print(banner)

def check_os():
    system = platform.system()
    print(f"{GREEN}[✓] İşletim Sistemi Tespit Edildi: {system}{RESET}")
    return system

def run_command(command, description, exit_on_error=True):
    print(f"{YELLOW}[*] {description}...{RESET}", end=" ")
    sys.stdout.flush()
    try:
        if ">" in command:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        else:
            args = command.split()
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"{GREEN}OK{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}HATA{RESET}")
        # Hata detayını göster
        if e.stderr:
             print(f"{RED}Hata Detayı:{RESET} {e.stderr.decode('utf-8')}")
        else:
             print(f"{RED}Hata Detayı:{RESET} {e}")
             
        if exit_on_error:
            print(f"{RED}Kurulum durduruldu.{RESET}")
            sys.exit(1)
        return False

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_and_install_brew():
    # Sadece macOS için
    try:
        subprocess.run(["brew", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"{GREEN}[✓] Homebrew yüklü.{RESET}")
    except:
        print(f"{YELLOW}[!] Homebrew bulunamadı. Redis kurulumu için Homebrew gereklidir.{RESET}")
        user_input = input(f"{YELLOW}[?] Homebrew kurulsun mu? (e/H): {RESET}")
        if user_input.lower() == 'e':
             print(f"{BLUE}Homebrew kuruluyor... (Bu işlem uzun sürebilir ve şifre isteyebilir){RESET}")
             os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        else:
             print(f"{RED}Homebrew olmadan devam edilemiyor.{RESET}")
             sys.exit(1)

def install_redis(os_type):
    print(f"\n{BLUE}--- REDIS KURULUMU ve AYARLARI ---{RESET}")
    
    redis_installed = False
    
    if os_type == "Darwin": # macOS
        check_and_install_brew()
        
        # 1. Redis kurulu mu kontrol et (Komut satırından)
        try:
             subprocess.run(["redis-server", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
             print(f"{GREEN}[✓] Redis zaten yüklü.{RESET}")
             redis_installed = True
        except:
             print(f"{YELLOW}[*] Redis bulunamadı. Homebrew ile kuruluyor...{RESET}")
             run_command("brew install redis", "Redis indiriliyor")
             redis_installed = True

        # 2. Servisi Başlat
        if redis_installed:
            if not check_port(6379):
                print(f"{YELLOW}[*] Redis servisi başlatılıyor...{RESET}")
                # brew services start redis genellikle asenkron çalışır, biraz bekleyelim
                subprocess.run(["brew", "services", "start", "redis"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(3)
            
            # 3. Test Et
            if check_port(6379):
                print(f"{GREEN}[✓] Redis Port 6379 üzerinde aktif!{RESET}")
            else:
                 print(f"{RED}[!] Redis servisi başlatılamadı. Manuel kontrol gerekebilir (`brew services list`){RESET}")
                 # Kritik hata değil, uygulama Redis'siz de çalışabilir (Fallback var)

    elif os_type == "Linux":
        print(f"{YELLOW}[!] Linux detected. Trying apt-get...{RESET}")
        run_command("sudo apt-get update && sudo apt-get install redis-server -y", "Redis kuruluyor", exit_on_error=False)
        run_command("sudo systemctl start redis-server", "Redis başlatılıyor", exit_on_error=False)

    else:
        print(f"{YELLOW}[!] Windows kurulumu exe ile yapılmalıdır. Redis adımı atlanıyor.{RESET}")

def manage_env_file():
    print(f"\n{BLUE}--- KONFİGÜRASYON (.env) ---{RESET}")
    if not os.path.exists(".env"):
        print(f"{YELLOW}[*] .env dosyası oluşturuluyor...{RESET}")
        with open(".env", "w") as f:
            f.write('DATABASE_URL="sqlite:///./bestwork.db"\n')
            f.write('SECRET_KEY="gizli_anahtar_buraya_gelecek_random_string_v10_1"\n')
            f.write('ALGORITHM="HS256"\n')
            f.write('ACCESS_TOKEN_EXPIRE_MINUTES=30\n')
            f.write('REDIS_URL="redis://localhost:6379/0"\n')
        print(f"{GREEN}[✓] .env dosyası oluşturuldu.{RESET}")
    else:
        # Mevcut .env'de REDIS_URL var mı kontrol et, yoksa ekle
        with open(".env", "r") as f:
            content = f.read()
        if "REDIS_URL" not in content:
            print(f"{YELLOW}[*] .env dosyasına REDIS_URL ekleniyor...{RESET}")
            with open(".env", "a") as f:
                f.write('\nREDIS_URL="redis://localhost:6379/0"\n')
        print(f"{GREEN}[✓] .env konfigürasyonu güncel.{RESET}")

def check_python_dependencies():
    print(f"\n{BLUE}--- PYTHON KÜTÜPHANELERİ ---{RESET}")
    print(f"{YELLOW}[*] Gerekli paketler yükleniyor (requirements.txt)...{RESET}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(f"{GREEN}[✓] Kütüphaneler başarıyla yüklendi.{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}[!] Kütüphane yüklenirken hata oluştu.{RESET}")
        sys.exit(1)

def init_db():
    print(f"\n{BLUE}--- VERİTABANI BAŞLATMA ---{RESET}")
    if os.path.exists("reset_db.py"):
        user_input = input(f"{YELLOW}[?] Veritabanını silip temiz kurulum yapmak ister misiniz? (e/H): {RESET}")
        if user_input.lower() == 'e':
            run_command(f"{sys.executable} reset_db.py", "Veritabanı sıfırlanıyor")
            print(f"{GREEN}[✓] Veritabanı ve örnek veriler hazır.{RESET}")
        else:
            print(f"{GREEN}[*] Veritabanı sıfırlama adımı atlandı.{RESET}")
    else:
        print(f"{RED}[!] reset_db.py bulunamadı. Veritabanı oluşturulamadı.{RESET}")

def main():
    print_banner()
    os_type = check_os()
    
    # 0. Sanal Ortam Kontrolü
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
         print(f"{RED}[UYARI] Sanal ortam (venv) aktif DEĞİL!{RESET}")
         print(f"{YELLOW}Sistem paketlerini bozmamak için önce 'source .venv/bin/activate' yapmanız önerilir.{RESET}")
         # Kullanıcıya sormadan devam etmeyelim, ama script takılmasın diye 'input' koyduk
         # Otomatik kurulumlarda bu input'u kaldırmak gerekebilir.

    # 1. Redis Kurulumu
    install_redis(os_type)

    # 2. .env Dosyası
    manage_env_file()

    # 3. Pip Install
    check_python_dependencies()

    # 4. DB Init
    init_db()

    print(f"\n{GREEN}==============================================={RESET}")
    print(f"{GREEN}   KURULUM BAŞARIYLA TAMAMLANDI! (v10.1)   {RESET}")
    print(f"{GREEN}==============================================={RESET}")
    print(f"\nSistemi başlatmak için şu komutu çalıştırın:")
    print(f"\n    {BLUE}uvicorn app.main:app --reload --port 8001{RESET}\n")

if __name__ == "__main__":
    main()
