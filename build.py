#!/usr/bin/env python3
"""Builds the offline iPad app (PWA) from src/player.html.

Run:  python3 build.py
Writes index.html, manifest.webmanifest, sw.js and icons/ next to this script.
"""
import pathlib, struct, zlib, hashlib, json

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src" / "player.html"

body = SRC.read_text(encoding="utf-8")
version = hashlib.sha1(body.encode()).hexdigest()[:10]

head = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<meta name="theme-color" content="#0e1114">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="HJ Player">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<link rel="icon" href="icons/icon-192.png">
<style>
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); box-sizing: border-box; height: 100%; }
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font: 14px system-ui, -apple-system, sans-serif; }
img { max-width: 100%; }
[hidden] { display: none !important; }
</style>
</head>
<body>
"""
tail = """
<script>
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
try { navigator.storage && navigator.storage.persist && navigator.storage.persist(); } catch (e) {}
</script>
</body>
</html>
"""
(HERE / "index.html").write_text(head + body + tail, encoding="utf-8")

(HERE / "manifest.webmanifest").write_text(json.dumps({
    "name": "Hidde Jager PLAYER",
    "short_name": "HJ Player",
    "start_url": "./",
    "scope": "./",
    "display": "fullscreen",
    "orientation": "any",
    "background_color": "#0e1114",
    "theme_color": "#0e1114",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}, indent=2), encoding="utf-8")

(HERE / "sw.js").write_text(f"""// Offline cache for Hidde Jager PLAYER. Version follows the page content.
const CACHE = 'hj-player-{version}';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png'];

self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Page itself: network first so updates arrive, cache when offline.
  if (req.mode === 'navigate') {{
    e.respondWith(fetch(req).then(r => {{ const copy = r.clone(); caches.open(CACHE).then(c => c.put('index.html', copy)); return r; }})
      .catch(() => caches.match('index.html')));
    return;
  }}
  // Everything else (icons, Google Fonts): cache first, fill cache on first use.
  if (url.origin === location.origin || /fonts\\.(googleapis|gstatic)\\.com$/.test(url.hostname)) {{
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {{
      const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return r;
    }})));
  }}
}});
""", encoding="utf-8")

# Icons: slate-blue fade-triangle on near-black, drawn without image libraries.
def png(size, path):
    gold_hi, gold, gold_lo, bg = (195, 216, 226), (143, 179, 196), (91, 125, 140), (14, 17, 20)
    m = size * 0.2
    x0, x1, y0, y1 = m, size - m, size * 0.27, size - size * 0.27
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            # triangle: left edge vertical, top-left corner to bottom-right corner (fade-out ramp)
            inside = x0 <= x <= x1 and y <= y1 and y >= y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            if inside:
                t = (y - y0) / (y1 - y0)
                c = tuple(int(gold_hi[i] * (1 - t) + gold[i] * t) if t < .6 else int(gold[i] * (1 - (t - .6) / .4 * .4) + gold_lo[i] * ((t - .6) / .4 * .4)) for i in range(3))
            else:
                c = bg
            row += bytes(c)
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(data)

(HERE / "icons").mkdir(exist_ok=True)
for s in (180, 192, 512):
    png(s, HERE / "icons" / f"icon-{s}.png")

print("built version", version)
