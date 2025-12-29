import http.server
import socketserver
import webbrowser
import sys
import os
import setup
import time
import urllib.parse

PORT = 8080

class SetupHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            is_installed = setup.check_installation()
            
            if is_installed:
                dynamic_content = """
                    <div class="alert">⚠️ Mevcut bir kurulum tespit edildi!</div>
                    <p>Ne yapmak istersiniz?</p>
                    <div class="btn-group">
                        <button class="btn-danger" onclick="startSetup('clean')">🗑️ Temiz Kurulum (Her Şeyi Sil)</button>
                        <button class="btn-primary" onclick="startSetup('repair')">🔧 Onar / Güncelle</button>
                    </div>
                """
            else:
                dynamic_content = """
                    <p>Sistemi otomatik olarak kurmak ve yapılandırmak için aşağıdaki butona tıklayın.</p>
                    <button class="btn-primary" onclick="startSetup('install')">🚀 Kurulumu Başlat</button>
                """

            # F-string yerine normal string kullanıyoruz ki JS/CSS süslü parantezleri karışmasın
            html_template = """
            <!DOCTYPE html>
            <html lang="tr">
            <head>
                <meta charset="UTF-8">
                <title>BestWork Kurulum</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; text-align: center; background: #f0f2f5; color: #333; }
                    .card { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; margin-bottom: 10px; }
                    p { color: #7f8c8d; margin-bottom: 30px; }
                    button { border: none; padding: 15px 30px; font-size: 16px; border-radius: 8px; cursor: pointer; transition: 0.3s; font-weight: bold; margin: 5px; }
                    .btn-primary { background: #3498db; color: white; }
                    .btn-primary:hover { background: #2980b9; transform: translateY(-2px); }
                    .btn-danger { background: #e74c3c; color: white; }
                    .btn-danger:hover { background: #c0392b; transform: translateY(-2px); }
                    button:disabled { background: #bdc3c7; cursor: not-allowed; transform: none; }
                    .alert { background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ffeeba; }
                    #log { margin-top: 30px; text-align: left; background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 8px; height: 250px; overflow-y: auto; font-family: 'Consolas', monospace; display: none; font-size: 14px; line-height: 1.5; }
                    .success { color: #2ecc71; font-weight: bold; }
                    .error { color: #e74c3c; font-weight: bold; }
                    .info { color: #3498db; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>🚀 BestWork Kurulum Sihirbazı</h1>
                    <div id="content">
                        <!-- DYNAMIC_CONTENT_HERE -->
                    </div>
                    <div id="log"></div>
                </div>
                <script>
                    async function startSetup(mode) {
                        const content = document.getElementById('content');
                        const log = document.getElementById('log');
                        
                        // Onay iste
                        if (mode === 'clean') {
                            if (!confirm("DİKKAT: Tüm veritabanı silinecek ve veriler kaybolacak! Emin misiniz?")) {
                                return;
                            }
                        }

                        // Butonları devre dışı bırak
                        const buttons = document.querySelectorAll('button');
                        buttons.forEach(btn => btn.disabled = true);
                        
                        log.style.display = 'block';
                        log.innerHTML = "<div>⏳ İşlem başlatılıyor...</div>";

                        try {
                            const response = await fetch('/run_setup?mode=' + mode, { method: 'POST' });
                            const reader = response.body.getReader();
                            const decoder = new TextDecoder();

                            while (true) {
                                const { value, done } = await reader.read();
                                if (done) break;
                                const text = decoder.decode(value);
                                const lines = text.split('\\n');
                                for (const line of lines) {
                                    if (line.trim()) {
                                        log.innerHTML += `<div>${line}</div>`;
                                        log.scrollTop = log.scrollHeight;
                                    }
                                }
                            }
                            
                            log.innerHTML += "<div class='success'><br>✨ İŞLEM BAŞARIYLA TAMAMLANDI!</div>";
                            log.innerHTML += "<div class='info'>Artık bu pencereyi kapatıp uygulamayı başlatabilirsiniz.</div>";
                            log.scrollTop = log.scrollHeight;
                        } catch (err) {
                            log.innerHTML += `<div class='error'><br>❌ HATA: ${err}</div>`;
                        }
                    }
                </script>
            </body>
            </html>
            """
            
            final_html = html_template.replace("<!-- DYNAMIC_CONTENT_HERE -->", dynamic_content)
            self.wfile.write(final_html.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/run_setup'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            mode = params.get('mode', ['install'])[0]

            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()

            def send_msg(msg):
                data = (msg + "\n").encode('utf-8')
                self.wfile.write(f"{len(data):X}\r\n".encode('utf-8'))
                self.wfile.write(data)
                self.wfile.write(b"\r\n")
                self.wfile.flush()

            try:
                if mode == 'clean':
                    send_msg("🧹 [0/3] Eski kurulum temizleniyor...")
                    setup.clean_database()
                    send_msg("✅ Temizlik tamamlandı.")
                    time.sleep(1)

                send_msg("📦 [1/3] Gerekli paketler kontrol ediliyor...")
                setup.install_dependencies()
                send_msg("✅ Paketler hazır.")
                time.sleep(1)

                send_msg("🗄️ [2/3] Veritabanı tabloları oluşturuluyor...")
                setup.initialize_database()
                send_msg("✅ Veritabanı tabloları hazır.")
                time.sleep(1)

                send_msg("🌱 [3/3] Örnek veriler ve Admin hesabı oluşturuluyor...")
                setup.seed_data()
                send_msg("✅ Veriler başarıyla eklendi.")

            except Exception as e:
                send_msg(f"❌ KRİTİK HATA: {str(e)}")
            
            self.wfile.write(b"0\r\n\r\n")

print(f"🚀 Kurulum sunucusu başlatıldı.")
print(f"👉 Tarayıcınız otomatik açılacak: http://localhost:{PORT}")

def open_browser():
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")

import threading
threading.Thread(target=open_browser).start()

with socketserver.TCPServer(("", PORT), SetupHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor.")
