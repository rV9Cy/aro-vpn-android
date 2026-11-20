# ARO VPN for Android (built in the cloud with GitHub Actions)

This builds an installable APK without Android Studio. The app is **v2rayNG** (open source, GPL-3.0) rebranded as ARO VPN
(name, icon, purple theme, own package id `ir.arrowdeveloper.arovpn`). It already supports: vless/vmess/trojan/shadowsocks/socks,
subscription links with auto update, QR / clipboard / file import, latency test, Per-App proxy (VpnService), DNS settings, auto-connect.

## Steps (Termux works)
1. Create an EMPTY **public** repo on github.com, e.g. `aro-vpn-android` (public = free unlimited build minutes, and GPL requires published source).
2. Create a token: GitHub > Settings > Developer settings > Personal access tokens (classic) > scope `repo`.
3. In Termux:
   ```
   pkg install git unzip
   unzip aro-android.zip && cd aro-android
   git config --global user.name "ArrowDeveloper" && git config --global user.email "you@example.com"
   git init -b main && git add -A && git commit -m "ARO Android"
   git remote add origin https://github.com/rv9cy/aro-vpn-android.git
   git push -u origin main        # username: rv9cy   password: the token
   ```
4. On github.com open the repo > **Actions** > "Build ARO VPN (Android)". The push starts it automatically (15-30 min the first time).
5. When it is green: open the run > **Artifacts** > `ARO-VPN-apk` > download, unzip, install the APK (allow "install unknown apps").

CPU: default `arm64-v8a` (nearly all phones). For another CPU use Actions > Run workflow and type it.

## Notes
- First builds sign with a temporary key. A later build with a different key cannot update over an installed one (uninstall first).
  To keep one key: add repository secrets `APP_KEYSTORE_BASE64`, `APP_KEYSTORE_PASSWORD`, `APP_KEYSTORE_ALIAS`, `APP_KEY_PASSWORD`.
- If a step fails, open it in the Actions log and send me the last ~30 lines.
- This changes only names/colors/icons/package id (see `tools/rebrand.py`); it is not the glass UI of the Windows/Termux version.
- License: derived from v2rayNG (GPL-3.0). Keep the source public and keep the credit.
