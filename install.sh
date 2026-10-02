#!/bin/bash

echo "[1/4] Aktualizacja pakietów i włączanie repozytorium universe..."
sudo add-apt-repository universe -y
sudo apt update

echo "[2/4] Instalowanie wymaganych zależności systemowych..."
sudo apt install -y python3-gi python3-gi-cairo python3-psutil python3-pil gir1.2-ayatana-appindicator3 fonts-dejavu

echo "[3/4] Kopiowanie pliku skryptu do katalogu domowego..."
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"
cp ram_indicator.py "$INSTALL_DIR/ram_indicator.py"
chmod +x "$INSTALL_DIR/ram_indicator.py"

echo "[4/4] Konfigurowanie autostartu..."
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat << EOF > "$AUTOSTART_DIR/ram-indicator.desktop"
[Desktop Entry]
Type=Application
Exec=python3 $INSTALL_DIR/ram_indicator.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Monitor RAM
Comment=Wskaźnik zużycia RAM, ZRAM i SWAP na pasku zadań
EOF

echo "Instalacja zakończona sukcesem! Skrypt uruchomi się automatycznie przy następnym logowaniu."
echo "Możesz go uruchomić już teraz wpisując: python3 $INSTALL_DIR/ram_indicator.py &"
