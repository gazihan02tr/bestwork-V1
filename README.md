# BestWork Network Marketing Sistemi

## Sürüm Geçmişi

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

