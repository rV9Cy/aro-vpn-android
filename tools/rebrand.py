#!/usr/bin/env python3
"""Rebrand a v2rayNG checkout as ARO VPN: app id, name, colors, launcher icons.
Usage: python3 tools/rebrand.py <path-to-v2rayNG-checkout>
Only literals/resources are changed (no Kotlin logic), so upstream still compiles."""
import re, sys, pathlib
from PIL import Image, ImageDraw

root = pathlib.Path(sys.argv[1]); app = root / 'V2rayNG/app'; res = app / 'src/main/res'
NAME, APPID, BG = 'ARO VPN', 'ir.arrowdeveloper.arovpn', (10, 9, 25, 255)
def need(cond, msg):
    if not cond: sys.exit('rebrand failed: ' + msg)

# 1) application id + apk file names
g = app / 'build.gradle.kts'; t = g.read_text(encoding='utf-8')
need('applicationId = "com.v2ray.ang"' in t, 'applicationId not found')
t = t.replace('applicationId = "com.v2ray.ang"', f'applicationId = "{APPID}"', 1).replace('"v2rayNG_', '"ARO-VPN_')
g.write_text(t, encoding='utf-8')

# 1b) code that compares the package name, and launcher shortcuts that hardcode it
u = app / 'src/main/java/com/v2ray/ang/util/Utils.kt'; t = u.read_text(encoding='utf-8')
old = 'BuildConfig.APPLICATION_ID.startsWith("com.v2ray.ang")'
need(old in t, 'isXray check not found')
u.write_text(t.replace(old, f'(BuildConfig.APPLICATION_ID.startsWith("com.v2ray.ang") || BuildConfig.APPLICATION_ID.startsWith("{APPID}"))'), encoding='utf-8')
sc = app / 'src/main/res/xml/shortcuts.xml'; t = sc.read_text(encoding='utf-8')
need('android:targetPackage="com.v2ray.ang"' in t, 'shortcuts targetPackage not found')
sc.write_text(t.replace('android:targetPackage="com.v2ray.ang"', f'android:targetPackage="{APPID}"'), encoding='utf-8')

# 2) app name in every language file
n = 0
for f in res.glob('values*/strings.xml'):
    s = f.read_text(encoding='utf-8'); s2 = re.sub(r'(<string name="app_name"[^>]*>)[^<]*(</string>)', r'\g<1>' + NAME + r'\g<2>', s)
    if s2 != s: f.write_text(s2, encoding='utf-8'); n += 1
need(n > 0, 'app_name not found')

# 3) Compose theme colors (hex literals only)
th = next(app.glob('src/main/java/com/v2ray/ang/ui/compose/Theme.kt')); s = th.read_text(encoding='utf-8')
LIGHT = dict(primary='7C3AED', onPrimary='FFFFFF', primaryContainer='EDE4FF', onPrimaryContainer='21005D', secondary='3B82F6', onSecondary='FFFFFF',
  secondaryContainer='DBE8FF', onSecondaryContainer='001B3E', tertiary='0891B2', tertiaryContainer='BDF1FF', onTertiaryContainer='001F28',
  surfaceTint='7C3AED', inversePrimary='C4B0FF', background='FBF9FF', surface='FBF9FF')
DARK = dict(primary='B79CFF', onPrimary='2A0A6B', primaryContainer='5B21B6', onPrimaryContainer='EDE4FF', secondary='7FB0FF', onSecondary='00315F',
  secondaryContainer='1E4E96', onSecondaryContainer='D8E6FF', tertiary='4FD8F0', onTertiary='00363F', tertiaryContainer='004E5C', onTertiaryContainer='BDF1FF',
  background='0A0919', surface='0A0919', surfaceTint='B79CFF', inversePrimary='7C3AED', surfaceContainerLowest='07061A', surfaceContainerLow='100E26',
  surfaceContainer='161331', surfaceContainerHigh='1D1A3E', surfaceContainerHighest='262249')
def patch(src, marker, colors):
    a = src.index(marker); b = src.index('\n)\n', a); blk = src[a:b]
    for k, v in colors.items():
        blk, c = re.subn(r'(\n\s+' + k + r' = Color\()0x[0-9A-Fa-f]{8}(\))', r'\g<1>0xFF' + v + r'\g<2>', blk)
        need(c == 1, f'color {k} not found in {marker}')
    return src[:a] + blk + src[b:]
s = patch(s, 'LightColor = lightColorScheme(', LIGHT); s = patch(s, 'DarkColor = darkColorScheme(', DARK)
th.write_text(s, encoding='utf-8')

# 4) launcher icons (same names/sizes as upstream)
def logo(size, scale):
    K = 4; S = size * K; g = Image.new('RGBA', (S, S))
    px = g.load()
    for y in range(S):
        for x in range(S):
            t = (x + y) / (2 * S); px[x, y] = (int(167 + (34 - 167) * t * 1.0), int(139 + (211 - 139) * t), int(250 + (238 - 250) * t), 255)
    m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m); u = S * scale / 40; ox = (S - 40 * u) / 2; oy = (S - 40 * u) / 2
    P = lambda x, y: (ox + x * u, oy + y * u)
    d.polygon([P(20, 3), P(36, 33), P(27, 33), P(20, 19), P(13, 33), P(4, 33)], fill=255); d.ellipse([*P(17, 26), *P(23, 32)], fill=0)
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0)); out.paste(g, (0, 0), m)
    return out.resize((size, size), Image.LANCZOS)
def full(size, round_):
    K = 4; S = size * K; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    (d.ellipse if round_ else (lambda b, fill: d.rounded_rectangle(b, S // 5, fill=fill)))([0, 0, S - 1, S - 1], fill=BG)
    im = im.resize((size, size), Image.LANCZOS); im.alpha_composite(logo(size, .62)); return im
done = 0
for f in res.glob('mipmap-*/ic_launcher*.png'):
    sz = Image.open(f).size[0]
    if f.name == 'ic_launcher_foreground.png': img = logo(sz, .56)      # adaptive: keep inside the safe zone
    elif f.name == 'ic_launcher_round.png': img = full(sz, True)
    elif f.name == 'ic_launcher.png': img = full(sz, False)
    else: continue
    img.save(f); done += 1
need(done >= 8, f'only {done} icons replaced')
(res / 'values/ic_launcher_background.xml').write_text('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#0A0919</color>\n</resources>\n')
print(f'ok: appId={APPID}, name in {n} files, theme patched, {done} icons')
