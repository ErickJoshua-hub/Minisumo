import network
import socket
import time
from neopixel import NeoPixel
from machine import Pin

# ─────────────────────────────────────────
#  NeoPixel en el pin 21
# ─────────────────────────────────────────
np = NeoPixel(Pin(21), 1)
np[0] = (0, 0, 0)
np.write()

# ─────────────────────────────────────────
#  Configuración del Access Point
# ─────────────────────────────────────────
SSID     = "ERICK"
PASSWORD = "12345678"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID, password=PASSWORD, authmode=network.AUTH_WPA2_PSK)

print("Iniciando Access Point...")
while not ap.active():
    time.sleep(0.1)

print("AP activo  ->  SSID: " + SSID)
print("IP: " + ap.ifconfig()[0])

# ─────────────────────────────────────────
#  Página HTML con 3 sliders RGB
# ─────────────────────────────────────────
HTML = """\
HTTP/1.1 200 OK\r
Content-Type: text/html; charset=utf-8\r
Connection: close\r
\r
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ESP32-S3 NeoPixel</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #0f0f1a;
      color: #e0e0e0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 20px;
    }
    .card {
      background: linear-gradient(135deg, #1a1a2e, #16213e);
      border: 1px solid #ffffff22;
      border-radius: 16px;
      padding: 40px 50px;
      text-align: center;
      box-shadow: 0 0 40px #00000066;
      max-width: 480px;
      width: 100%;
    }
    h1 { font-size: 1.8rem; color: #fff; margin-bottom: 6px; }
    .subtitle { color: #888; margin-bottom: 30px; font-size: 0.9rem; }

    /* Preview del color */
    #preview {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      margin: 0 auto 28px auto;
      background: rgb(0,0,0);
      box-shadow: 0 0 30px rgba(0,0,0,0.8);
      border: 3px solid #ffffff18;
      transition: background 0.15s, box-shadow 0.15s;
    }

    /* Sliders */
    .slider-group { margin-bottom: 20px; text-align: left; }
    .slider-group label {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      margin-bottom: 6px;
    }
    .slider-group label span { color: #aaa; font-weight: 400; }
    input[type=range] {
      -webkit-appearance: none;
      width: 100%;
      height: 8px;
      border-radius: 4px;
      outline: none;
      cursor: pointer;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: 2px solid #fff;
      cursor: pointer;
    }
    #rSlider { background: linear-gradient(to right,#1a0000,#ff0000); }
    #rSlider::-webkit-slider-thumb { background: #ff4444; }
    #gSlider { background: linear-gradient(to right,#001a00,#00ff00); }
    #gSlider::-webkit-slider-thumb { background: #44ff44; }
    #bSlider { background: linear-gradient(to right,#00001a,#0000ff); }
    #bSlider::-webkit-slider-thumb { background: #4488ff; }

    .status {
      margin-top: 24px;
      padding: 10px 16px;
      background: #0a2a0a;
      border: 1px solid #00ff6633;
      border-radius: 10px;
      color: #00ff66;
      font-size: 0.8rem;
      letter-spacing: 0.5px;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>&#x1F4A1; NeoPixel RGB</h1>
    <p class="subtitle">ESP32-S3 &mdash; Pin 21</p>

    <div id="preview"></div>

    <div class="slider-group">
      <label>RED <span id="rVal">0</span></label>
      <input type="range" id="rSlider" min="0" max="255" value="0">
    </div>
    <div class="slider-group">
      <label>GREEN <span id="gVal">0</span></label>
      <input type="range" id="gSlider" min="0" max="255" value="0">
    </div>
    <div class="slider-group">
      <label>BLUE <span id="bVal">0</span></label>
      <input type="range" id="bSlider" min="0" max="255" value="0">
    </div>

    <div class="status" id="status">&#x2705; Conectado</div>
  </div>

  <script>
    const rSlider = document.getElementById('rSlider');
    const gSlider = document.getElementById('gSlider');
    const bSlider = document.getElementById('bSlider');
    const preview = document.getElementById('preview');
    const statusEl = document.getElementById('status');
    let debounce;

    function updatePreview() {
      const r = rSlider.value, g = gSlider.value, b = bSlider.value;
      document.getElementById('rVal').textContent = r;
      document.getElementById('gVal').textContent = g;
      document.getElementById('bVal').textContent = b;
      preview.style.background = `rgb(${r},${g},${b})`;
      const glow = `0 0 30px rgba(${r},${g},${b},0.7)`;
      preview.style.boxShadow = glow;
    }

    function sendColor() {
      const r = rSlider.value, g = gSlider.value, b = bSlider.value;
      fetch(`/color?r=${r}&g=${g}&b=${b}`)
        .then(res => {
          statusEl.textContent = res.ok ? '\\u2705 Color aplicado' : '\\u26A0\\uFE0F Error';
        })
        .catch(() => { statusEl.textContent = '\\u274C Sin respuesta'; });
    }

    [rSlider, gSlider, bSlider].forEach(s => {
      s.addEventListener('input', () => {
        updatePreview();
        clearTimeout(debounce);
        debounce = setTimeout(sendColor, 80);
      });
    });

    updatePreview();
  </script>
</body>
</html>
"""

# ─────────────────────────────────────────
#  Respuesta HTTP simple (200 vacío)
# ─────────────────────────────────────────
OK_RESPONSE = "HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"

# ─────────────────────────────────────────
#  Servidor Web (socket TCP en puerto 80)
# ─────────────────────────────────────────
# Reintentar si el puerto 80 todavía está ocupado (reinicios rápidos)
for _intento in range(10):
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(("", 80))
        servidor.listen(5)
        break
    except OSError:
        print("Puerto 80 ocupado, reintentando...")
        try: servidor.close()
        except: pass
        time.sleep(2)
else:
    raise OSError("No se pudo abrir el puerto 80 tras varios intentos")

print("Servidor web escuchando en el puerto 80...")
print("Conectate a 'ERICK' y abre http://192.168.4.1")

while True:
    try:
        cliente, addr = servidor.accept()
        peticion = cliente.recv(2048).decode("utf-8", "ignore")

        # Detectar ruta /color?r=&g=&b=
        if "GET /color" in peticion:
            # Extraer valores de la query string
            try:
                qs = peticion.split("GET /color?")[1].split(" ")[0]
                params = {}
                for par in qs.split("&"):
                    k, v = par.split("=")
                    params[k] = int(v)
                r = max(0, min(255, params.get("r", 0)))
                g = max(0, min(255, params.get("g", 0)))
                b = max(0, min(255, params.get("b", 0)))
                np[0] = (r, g, b)
                np.write()
                print("Color -> R:{} G:{} B:{}".format(r, g, b))
            except Exception as e:
                print("Error parseo color:", e)
            cliente.send(OK_RESPONSE)
        else:
            # Servir la página principal
            cliente.send(HTML)

        cliente.close()
    except OSError as e:
        print("Error de socket:", e)
        try:
            cliente.close()
        except:
            pass