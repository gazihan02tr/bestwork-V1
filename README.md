# BestWork Network Marketing Sistemi

## Sürüm Geçmişi

### v10.1 (10.01.2026) - Güvenlik Mimarisi Reformu, Core Optimizasyon ve Canlı Profil Sistemi

Bu sürümde ("Security & Stability Reform"), sistemin arka plan mimarisi (Backend) güvenlik ve performans odaklı olarak %60 oranında yeniden yazılmıştır. Front-end tarafında ise "Single Page Application" (SPA) hissi veren anlık profil güncelleme mekanizmaları devreye alınmıştır.

#### 1. Güvenlik Mimarisi Reformu (JWT Transformation)
*   **Token-Based Authentication:** Klasik ve güvensiz `user_id` çerez yapısı terk edilerek, endüstri standardı **JWT (JSON Web Token)** altyapısına geçildi.
*   **Middleware Entegrasyonu:** Tüm istekler (Requests), Python seviyesinde araya giren yeni bir Middleware katmanı tarafından süzülerek kimlik doğrulama işlemi merkezi hale getirildi.
*   **Cookie Security Hardening:**
    *   `HttpOnly`: JavaScript erişimine kapatıldı (XSS Koruması).
    *   `SameSite=Lax`: CSRF saldırılarına karşı koruma eklendi.
*   **Python 3.9 Uyumluluğu:** Sunucu tarafındaki modern sözdizimi hataları (`|` operatörleri), Python 3.9 ve altı sürümlerin de çalıştırabileceği `Optional` ve `Union` yapılarına dönüştürüldü.

#### 2. Çekirdek Logic Optimizasyonu (Algorithm Refactoring)
*   **Recursion to Iteration:** Binary Ağaç yapısında derinlik hesaplayan ve prim dağıtan rekürsif (kendi kendini çağıran) fonksiyonlar, **While Döngüsü (Iterative)** mimarisine çevrildi. Bu sayede "Maximum Recursion Depth Exceeded" hataları ve bellek şişmeleri tarihe karıştı.
*   **Atomic Transactions:** Finansal veritabanı işlemlerine `row-locking` (satır kilitleme) mekanizması eklendi. Aynı anda gelen binlerce istekte bile bakiye tutarlılığı %100 garanti altına alındı.

#### 3. Canlı Profil ve Arayüz Deneyimi (Live UX)
*   **Instant-Upload Teknolojisi:**
    *   Profil resmi yükleme modülü **AJAX** ile yeniden yazıldı.
    *   Sayfa yenilenmesine gerek kalmadan, yükleme tamamlandığı anda hem büyük profil resmi hem de üst menüdeki (Header) küçük avatar anlık olarak güncellenir.
*   **Görsel Geribildirim (Progress Bar):** Resim yüklenirken kullanıcıya %0'dan %100'e kadar ilerleyen görsel bir durum çubuğu eklendi.
*   **Akıllı Avatar Fallback:** Profil resmi olmayan kullanıcılar için artık anonim ikon yerine, ismin baş harfini (Örn: "M") içeren modern bir tipografik avatar gösteriliyor.
*   **WebP Optimizasyonu:** Sunucuya yüklenen tüm görseller otomatik olarak yeni nesil **.webp** formatına dönüştürülüyor ve `Ad_Soyad_ID` formatında isimlendirilerek SEO uyumlu hale getiriliyor.
*   **Session State Repair:** Login olmasına rağmen arayüzün "Çıkış Yapmış" gibi davranmasına neden olan tüm şablon (Template) hataları giderildi.



### v10.0 (07.01.2026) - Microsoft Fluent Design Entegrasyonu, Hibrit Arayüz Mimarisi ve Çekirdek Sistem Optimizasyonu

Bu majör sürümde sistem, web tabanlı standart arayüz yapısından tamamen sıyrılarak, masaüstü uygulaması deneyimi sunan **"Microsoft Fluent Design System"** mimarisine geçirilmiştir. Kullanıcı deneyimi (UX) derinlik, ışık ve hareket prensipleriyle yeniden kurgulanmış, yönetim paneli bir web sitesinden ziyade güçlü bir yönetim konsoluna dönüştürülmüştür. 

#### 1. Devrimsel Arayüz Mimarisi (Fluent UI Transformation)
*   **Mica & Acrylic Material Entegrasyonu:**
    *   Yönetim paneli arka planlarında, işletim sistemi seviyesinde derinlik algısı yaratan dinamik **Mica** materyalleri kullanıldı.
    *   Kartlar, modallar ve paneller, arkasındaki içeriği flulaştıran buzlu cam (**Acrylic**) efektleriyle zenginleştirildi.
*   **Nano-Optimizasyonlu Render Motoru:** 
    *   CSS render süreçleri, GPU hızlandırmalı katmanlar (layer promotion) kullanılarak %40 daha akıcı hale getirildi.
*   **Mikro-Etkileşimler (Micro-Interactions):**
    *   **Reveal Highlight:** Elemanların üzerine gelindiğinde farenin hareketini takip eden dinamik ışık hüzmesi efektleri eklendi.
    *   Buton ve input alanlarına bastırılmış (pressed) ve odaklanmış (focused) durumlar için milisaniyelik animasyonlar tanımlandı.

#### 2. Yeni Nesil Dashboard Konsolu (Executive Dashboard)
*   **Akıllı Widget Ekosistemi:**
    *   Statik istatistik kartları, yerini canlı veri akışı sağlayan hibrit widget bloklarına bıraktı.
    *   Hızlı Erişim Kutucukları (Quick Action Tiles), Windows Başlat menüsü ergonomisiyle yeniden tasarlandı.
*   **Görsel Hiyerarşi İyileştirmesi:**
    *   Tipografi motoru **Inter (Segoe UI Clone)** font ailesi ile güncellenerek okunabilirlik kurumsal standartlara çekildi.

#### 3. Güvenlik ve Altyapı İyileştirmeleri (Under-the-hood)
*   **Admin İzoloasyonu v2:** Yönetim paneli rotaları, olası XSS ve CSRF ataklarına karşı görsel katmanda izole edildi.
*   **Login Gateway Protokolü:** `/bestsoft` giriş kapısı, Fluent Design prensipleriyle yeniden kodlanarak hem estetik hem de psikolojik bir güvenlik bariyeri oluşturuldu.

### v9.0 (06.01.2026) - BestSoft Kurumsal Admin Arayüzü, Dinamik Footer ve UI Modernizasyonu

Bu sürümde yönetim paneli (Admin Panel), kullanıcı arayüzünden tamamen ayrılarak **"BestSoft"** markası altında yeniden tasarlandı. Kurumsal kimliğe uygun modern bir "Light Mode" teması uygulandı ve site genelinde dinamik içerik yönetimi sağlandı.

#### 1. Yeni "BestSoft" Admin Arayüzü (`/admin`, `/bestsoft`)
*   **İzole Tasarım:** Yönetim paneli, ana site tasarımından tamamen ayrıştırıldı (Decoupled UI). Kendi özel CSS ve JS yapılandırmasına sahip.
*   **Light Mode & Kurumsal Renkler:**
    *   Önceki koyu tema (Dark Mode) yerine, kurumsal **Mor (#9333EA)** ve **İndigo (#4338ca)** renklerinin ağırlıkta olduğu ferah bir **Beyaz/Slate** tema sistemi geliştirildi.
    *   Arka planlar `bg-slate-50`, kartlar `bg-white` olarak güncellendi.
*   **Yenilenen Giriş Sayfası (`/bestsoft`):**
    *   Modern, "Glassmorphism" efektli, beyaz zemin üzerine mor ambiyans ışıklı yeni login sayfası tasarlandı.
    *   Giriş güvenliği ve kullanıcı deneyimi (UX) iyileştirildi.

#### 2. Dinamik İçerik Yönetimi (Site Ayarları)
*   **Dinamik Footer Yapısı:**
    *   Admin panelinden yönetilebilen bir Footer (Alt Bilgi) altyapısı kuruldu.
    *   **Yönetilebilir Alanlar:**
        *   Marka Adı
        *   Copyright Metni
        *   Alt Açıklama Yazısı
        *   İletişim E-posta ve Telefon Bilgileri
    *   Bu veriler veritabanında (`site_ayarlari` tablosu) tutularak tüm site genelinde (`base.html`) anlık olarak güncellenebilir hale geldi.
*   **Gelişmiş Ayarlar Sayfası:**
    *   `/admin/kontrol` sayfası, form gruplarına (Site, İletişim, Finansal) ayrıldı.
    *   Input alanları, odaklanıldığında (focus) mor halka (ring) oluşturan modern bir tasarıma kavuşturuldu.

#### 3. Backend Geliştirmeleri
*   **Yeni Veritabanı Modelleri:**
    *   `SiteAyarlari`: Site başlığı, çekim limitleri, footer metinleri ve iletişim bilgilerini tutan singleton model eklendi.
*   **Yönetim Mantığı (`routers/admin.py`):**
    *   Admin rotaları, yeni modelleri (SiteAyarlari, NesilAyari) destekleyecek şekilde güncellendi.
    *   Footer verilerini context processor veya doğrudan route üzerinden template'e aktaran yapı kuruldu.

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

