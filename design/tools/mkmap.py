"""Maakt de Europakaart voor netwerk.html uit Natural Earth-data (npm world-atlas@2, countries-50m.json).

Gebruik:  python3 tools/mkmap.py <pad/naar/countries-50m.json>
Schrijft: partials/europe-map.svg (landen als paden) en partials/dealers.json (dealers + x/y op de kaart).
Projectie: Lambert azimutaal oppervlaktegetrouw, gecentreerd op 10°O 52°N.
"""
import json, math, sys

W, H = 1000, 860
LON0, LAT0 = math.radians(10), math.radians(52)
SCALE = 1500
CX, CY = 542, 460
PARTNER = {'040', '056', '100', '191', '208', '246', '250', '276', '300', '348', '352', '380', '616', '620', '703', '724', '752', '756', '528', '826'}


def proj(lon, lat):
    l, p = math.radians(lon), math.radians(lat)
    k = math.sqrt(2 / (1 + math.sin(LAT0) * math.sin(p) + math.cos(LAT0) * math.cos(p) * math.cos(l - LON0)))
    x = k * math.cos(p) * math.sin(l - LON0)
    y = k * (math.cos(LAT0) * math.sin(p) - math.sin(LAT0) * math.cos(p) * math.cos(l - LON0))
    return CX + x * SCALE, CY - y * SCALE


topo = json.load(open(sys.argv[1]))
sx, sy = topo['transform']['scale']
tx, ty = topo['transform']['translate']
arcs = []
for arc in topo['arcs']:
    x = y = 0
    pts = []
    for dx, dy in arc:
        x += dx; y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)


def ring(idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def path(rings):
    out = []
    for r in rings:
        if not any(-32 < lo < 46 and 33 < la < 72 for lo, la in r):
            continue
        last, seg = None, []
        for lo, la in r:
            if lo < -40 or lo > 60:
                continue
            x, y = proj(lo, la)
            if last and abs(x - last[0]) + abs(y - last[1]) < 1.1:
                continue
            seg.append(f'{x:.1f},{y:.1f}')
            last = (x, y)
        if len(seg) > 2:
            out.append('M' + 'L'.join(seg) + 'Z')
    return ''.join(out)


parts = []
for g in topo['objects']['countries']['geometries']:
    if g.get('type') not in ('Polygon', 'MultiPolygon'):
        continue
    polys = [g['arcs']] if g['type'] == 'Polygon' else g['arcs']
    d = ''.join(path([ring(r) for r in poly]) for poly in polys)
    if not d:
        continue
    cls = 'c p' if g.get('id') in PARTNER else 'c'
    name = g.get('properties', {}).get('name', '')
    parts.append(f'<path class="{cls}" data-n="{name}" d="{d}"/>')

svg = (f'<svg class="map__svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
       + ''.join(parts) + '</svg>')
open('partials/europe-map.svg', 'w').write(svg)

data = json.load(open('data/dealers.json'))
for d in data['europe']:
    x, y = proj(d['lng'], d['lat'])
    d['x'], d['y'] = round(x / W * 100, 2), round(y / H * 100, 2)
json.dump(data, open('partials/dealers.json', 'w'), ensure_ascii=False)
print(f'europe-map.svg {len(svg) // 1024} KB, {len(parts)} landen; dealers.json {len(data["europe"])} vestigingen')
