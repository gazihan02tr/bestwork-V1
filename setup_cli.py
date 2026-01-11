import os
import sys
import subprocess
import time
import platform

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print("""
  ____            _   ____          __ _   
 | __ )  ___  ___| |/ ___|   ___  / _| |_ 
 |  _ \ / _ \/ __| |\___ \  / _ \| |_| __|
 | |_) |  __/\__ \ |_ ___) || (_) |  _| |_ 
 |____/ \___||___/\__|____/  \___/|_|  \__|
    """)
    print("   BESTSOFT AĞ YÖNETİM SİSTEMİ - KURULUM v26.1.0")
    print("-" * 50)

def install_requirements():
    print("\n>> Kütüphaneler yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n[OK] Kurulum başarıyla tamamlandı.")
    except subprocess.CalledProcessError as e:
        print(f"\n[HATA] Kurulum sırasında bir sorun oluştu: {e}")

def reset_db():
    print("\n>> Veritabanı sıfırlanıyor...")
    try:
        subprocess.check_call([sys.executable, "reset_db_v2.py"])
        print("\n[OK] Veritabanı başarıyla oluşturuldu.")
    except subprocess.CalledProcessError as e:
        print(f"\n[HATA] Veritabanı hatası: {e}")

def start_server():
    print("\n>> Sunucu başlatılıyor...")
    url = "http://127.0.0.1:8000/bestsoft"
    
    # Tarayıcıyı aç
    time.sleep(1)
    if platform.system() == "Darwin":
        subprocess.call(["open", url])
    elif platform.system() == "Windows":
        os.system(f"start {url}")
        
    # Uvicorn'u başlat
    try:
        subprocess.call([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"])
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")

def main():
    while True:
        print_header()
        print("1. Sıfırdan Kurulum Yap (Kütüphaneler + DB)")
        print("2. Sadece Veritabanını Sıfırla")
        print("3. Sistemi Başlat")
        print("4. Çıkış")
        print("-" * 50)
        
        choice = input("Seçiminiz (1-4): ")
        
        if choice == '1':
            install_requirements()
            reset_db()
            input("\nDevam etmek için Enter'a basın...")
        elif choice == '2':
            confirm = input("Tüm veriler silinecek. Emin misiniz? (e/h): ")
            if confirm.lower() == 'e':
                reset_db()
            else:
                print("İptal edildi.")
            input("\nDevam etmek için Enter'a basın...")
        elif choice == '3':
            start_server()
            input("\nDevam etmek için Enter'a basın...")
        elif choice == '4':
            print("Çıkış yapılıyor...")
            sys.exit()
        else:
            input("Geçersiz seçim. Tekrar denemek için Enter'a basın...")

if __name__ == "__main__":
    main()
