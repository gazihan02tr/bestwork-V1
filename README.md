# BestWork Network Marketing Sistemi

## Sürüm Geçmişi

### v8.0 (04.01.2026) - Mimari Refactoring, Güvenlik ve Kullanıcı Paneli Genişletmesi

Bu sürümde sistemin altyapısı tamamen modernize edilmiş, güvenlik açıkları kapatılmış, kod tabanı modüler hale getirilmiş ve kullanıcı paneli yeni sayfalarla zenginleştirilmiştir.

#### 1. Yeni Dashboard Sayfaları
*   **Üyelik Bilgilerim (`/uyelik-bilgileri`):**
    *   Kullanıcının tüm profil detaylarını (Kişisel bilgiler, İletişim, Üyelik durumu, Sponsor bilgisi) gösteren kart yapısında yeni sayfa eklendi.
*   **Prim Detayları (`/prim-bilgileri`):**
    *   Kullanıcının prim kazançlarını detaylı inceleyebileceği sayfa oluşturuldu.
    *   Ay ve Yıl bazlı filtreleme altyapısı eklendi.
*   **Hızlı Başlangıç Bonusu (`/hizli-baslangic`):**
    *   Hızlı başlangıç bonuslarını listeleyen, paket ve tarih detaylı tablo sayfası eklendi.
*   **Referans Bonusu (`/referans-bonusu`):**
    *   Referans gelirlerinin listelendiği, arama ve tarih filtreli sayfa eklendi.

#### 2. Navigasyon ve Arayüz (UI/UX) İyileştirmeleri
*   **Breadcrumb (Ekmek Kırıntısı) Yapısı:**
    *   Kullanıcı deneyimini artırmak için aşağıdaki sayfalara "Anasayfa / [Sayfa Adı]" şeklinde navigasyon çubuğu eklendi:
        *   Varis İşlemleri
        *   Banka Bilgileri
        *   Şifre Değiştir
        *   Kariyer Takibi
        *   Üyelik Bilgilerim
        *   Prim Detayları
        *   Hızlı Başlangıç
        *   Referans Bonusu
*   **Menü Entegrasyonu:**
    *   Üst menüdeki "Kişisel" ve "Bonuslar" dropdown menüleri yeni sayfalarla güncellendi.
    *   User Control Bar (Panel içi menü) görünürlük kuralları yeni sayfaları kapsayacak şekilde genişletildi.
*   **Görsel Düzenlemeler:**
    *   Banka Bilgileri ve Varis İşlemleri formlarındaki butonların metin renkleri okunabilirlik için beyaza sabitlendi.

#### 3. İş Mantığı ve Kısıtlamalar
*   **Tek Banka Hesabı Kuralı:**
    *   Kullanıcıların sisteme sadece **1 adet** banka hesabı ekleyebilmesi kuralı getirildi.
    *   Mevcut hesap varken yeni ekleme butonu gizleniyor/engelleniyor.
    *   Hesap silindiğinde tekrar ekleme hakkı açılıyor.

#### 4. Mimari Değişiklikler (Refactoring)
*   **Router Pattern'e Geçiş:** Monolitik `main.py` yapısı terk edildi. Uygulama mantığı modüllere ayrıldı:
    *   `app/routers/auth.py`: Kimlik doğrulama işlemleri.
    *   `app/routers/mlm.py`: Ağaç yapısı ve network marketing mantığı.
    *   `app/routers/shop.py`: E-ticaret, sepet ve sipariş işlemleri.
    *   `app/routers/admin.py`: Yönetim paneli işlemleri.
    *   `app/routers/dashboard.py`: Kullanıcı paneli ve raporlar.
*   **Bağımlılık Yönetimi:** Veritabanı ve template bağımlılıkları `app/dependencies.py` altında merkezileştirildi.

#### 5. Güvenlik İyileştirmeleri
*   **Şifre Hashleme:** Kullanıcı şifrelerinin veritabanında düz metin (plain text) olarak saklanması engellendi.
    *   `passlib` ve `bcrypt` kütüphaneleri entegre edildi.
    *   Kayıt ve şifre değiştirme işlemlerinde otomatik hashleme devreye alındı.
*   **Güvenli Oturum:** Giriş işlemleri `app/utils.py` üzerindeki güvenli doğrulama fonksiyonlarına bağlandı.

#### 6. Temizlik ve Düzenlemeler
*   **Kod Temizliği:** `main.py` dosyası 900+ satırdan ~100 satıra düşürüldü.
*   **Dosya Temizliği:** Kullanılmayan eski şablon dosyaları (`_old.html` uzantılı) sistemden kaldırıldı.
*   **Sabitler:** Rütbe gereksinimleri gibi konfigürasyon verileri `app/utils.py` dosyasına taşındı.

### v7.0 (03.01.2026) - Kapsamlı Sistem Güncellemesi ve Optimizasyonlar

Bu sürümde kullanıcı arayüzü (UI), veritabanı mantığı ve sistem yerelleştirmesi üzerinde önemli iyileştirmeler yapılmıştır.

#### 1. Arayüz (Frontend) İyileştirmeleri
*   **Dashboard (Panel):**
    *   Büyük sayıların gösterimi optimize edildi (örn: 1.500.000 -> 1.5M, 150.000 -> 150K).
    *   "Sonraki Seviye" gösterimi düzeltildi; en üst rütbeye (Triple President) ulaşan kullanıcılar için gereksiz "Sonraki: ..." yazısı kaldırıldı.
*   **Kariyer Takibi Sayfası:**
    *   **Dark Mode:** Karanlık mod uyumluluğu tam olarak sağlandı. Renk paleti, arka planlar ve metinler koyu tema için optimize edildi.
    *   **Görsel İyileştirme:** Rütbe kartları için özel renk tanımları (Platinum: Slate, Pearl: Rose, vb.) yapıldı.
    *   **PV Gösterimi:** Hedef PV'yi aşan durumlarda (örn: 100M PV var, hedef 5K), ilerleme çubuğunun bozulmaması için gösterilen değer hedefe sabitlendi (5.000 / 5.000 PV).
*   **Soy Ağacı (Binary Tree):**
    *   Sayfa yüklenirken "Veriler yükleniyor..." yazısında takılma sorunu (eski JS kodlarından kaynaklı) giderildi.
    *   Gereksiz kenar çubuğu (sidebar) kaldırıldı, tam ekran deneyimi sağlandı.

#### 2. Backend ve İş Mantığı Güncellemeleri
*   **ID Üretim Mantığı:**
    *   Sıralı ID (900000001, 900000002...) yerine **Rastgele ID** (90xxxxxxx) sistemine geçildi.
*   **Saat Dilimi (Timezone):**
    *   Sistemdeki tüm tarih/saat kayıtları (Kayıt Tarihi, Sipariş Tarihi, Loglar vb.) **Türkiye Saati (Europe/Istanbul)** ile senkronize edildi.
    *   Veritabanı modelleri `DateTime(timezone=True)` yapısına geçirildi.
*   **Rütbe Sistemi:**
    *   Rütbe isimleri güncellendi ve standartlaştırıldı (Presidential -> President).

#### 3. Veritabanı ve Kurulum
*   **Sıfırlama Scripti (`reset_db.py`):**
    *   "Süper Admin" hesabı varsayılan olarak eklendi:
        *   **İsim:** BestWork
        *   **Rütbe:** Triple President
        *   **Kariyer Puanı:** 100.000.000 PV (Sol/Sağ)
        *   **Anlık Bakiye:** 0 (Temiz başlangıç için)
*   **Kurulum Sihirbazı (`installer_wizard.py`):**
    *   Yeni ID mantığı ve Türkiye saati ayarları kurulum sihirbazına entegre edildi.

---

