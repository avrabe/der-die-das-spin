# 🦫 Quick Start Guide - Der Die Das Capybara Game!

## For Your Daughter! 🎮✨

Ein lustiges Deutsch-Lernspiel mit Capybaras im Roblox-Stil!

---

## 🚀 Start in 3 Schritten

### 1. Installiere Spin (einmalig)
```bash
curl -fsSL https://developer.fermyon.com/downloads/install.sh | bash
rustup target add wasm32-wasip1
```

### 2. Starte das Spiel
```bash
cd der-die-das-spin
spin up
```

### 3. Öffne im Browser
```
http://localhost:3000
```

Das wars! 🎉

---

## 🧪 Teste alles mit einem Klick

Nach `spin up` in einem neuen Terminal:

```bash
./verify_game.sh
```

Dieser Script testet automatisch:
- ✅ Random Word API
- ✅ Multiplayer Session erstellen
- ✅ Session beitreten
- ✅ Antworten senden
- ✅ Scores aktualisieren
- ✅ Capybara Theme
- ✅ Alle Static Files

---

## 🎮 Spiel-Modi für deine Tochter

### 1. 📚🦫 Übungs-Modus
- Keine Zeitbegrenzung
- Lernen in Ruhe
- Perfekt zum Üben!

### 2. ⏱️🦫 Zeit-Challenge
- 2 Minuten
- So viele Wörter wie möglich
- Schnell sein wie ein Capybara!

### 3. 🎮🦫 Multiplayer Erstellen
- Spiel erstellen
- Session ID kopieren
- Freund einladen

### 4. 🔗🦫 Multiplayer Beitreten
- Session ID eingeben
- Gegeneinander spielen
- Live Scores sehen!

---

## 🦫 Capybara Features

- **Überall Capybaras!** 🦫 Emojis auf jedem Button
- **Roblox-Style!** 3D-Blöcke wie in Roblox
- **Bunte Farben!** Orange, Gelb, Grün, Blau, Pink
- **Comic Sans!** Die lustige Spiel-Schrift
- **Animationen!** Capybaras hüpfen und schweben
- **Deutsch!** Alle Texte auf Deutsch zum Lernen

---

## 📱 Funktioniert überall

- ✅ Computer (große Buttons)
- ✅ Tablet (Touch-optimiert)
- ✅ Handy (responsive Design)

---

## 🔧 Entwicklung

### Bauen
```bash
cd der-die-das-spin
cargo build --target wasm32-wasip1 --release
spin build
```

### Testen
```bash
# Native tests
cargo test --target x86_64-unknown-linux-gnu

# API tests
./verify_game.sh
```

### Datenbank ansehen
```bash
sqlite3 .spin/sqlite_db.db
SELECT nominativ_singular, genus FROM derdiedas LIMIT 10;
.quit
```

---

## 📚 Mehr Infos

- **CAPYBARA_THEME.md** - Alle Theme-Details für Kinder
- **TESTING.md** - Komplette Test-Dokumentation
- **README.md** - Technische Dokumentation

---

## 🎨 Was deine Tochter liebt

### Capybaras 🦫
- Capybara-Titel
- Capybara-Untertitel
- Capybara auf jedem Button
- Schwimmende Capybaras im Hintergrund
- Capybara-Animationen bei richtig/falsch
- Capybara-Farben (Orange, Braun, Gelb)

### Roblox-Style 🎮
- 3D-Buttons mit Schatten
- Bunte Block-Farben
- Bouncy Click-Effekt
- Comic Sans Schrift
- Glanz-Effekte auf Buttons

---

## 🏆 Erfolgs-Nachrichten

- 🦫🏆 **Du hast gewonnen!** 🎉
- 🦫💪 **Gegner gewinnt!** Weiter üben!
- 🦫🤝 **Unentschieden!** Gut gespielt!
- 🦫 **Super gemacht!**

---

## ❤️ Made with Love

Made with 💖 for kids who love capybaras and Roblox!

**Viel Spaß beim Deutsch Lernen mit den Capybaras!** 🦫✨

---

## 🐛 Probleme?

### Server startet nicht?
```bash
# Port schon belegt? Andere Port verwenden:
spin up --listen 127.0.0.1:3001
```

### Keine Wörter?
```bash
# Datenbank prüfen:
sqlite3 .spin/sqlite_db.db "SELECT COUNT(*) FROM derdiedas;"
```

### Tests schlagen fehl?
```bash
# Sicherstellen dass Server läuft:
curl http://localhost:3000/api/entry.json
```

---

**Fertig! Jetzt kann deine Tochter Deutsch lernen und Spaß haben!** 🎉🦫
