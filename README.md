# 🦫 Der Die Das - Capybara Deutsch Spiel!

[![Rust](https://github.com/avrabe/der-die-das-spin/actions/workflows/rust-native.yml/badge.svg)](https://github.com/avrabe/der-die-das-spin/actions/workflows/rust-native.yml)
[![Release](https://github.com/avrabe/der-die-das-spin/actions/workflows/release.yml/badge.svg)](https://github.com/avrabe/der-die-das-spin/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/avrabe/der-die-das-spin/graph/badge.svg?token=jywfs1sW4p)](https://codecov.io/gh/avrabe/der-die-das-spin)

Ein lustiges Deutsch-Lernspiel mit Capybaras im Roblox-Stil! 🎮✨

Learn German articles (der/die/das) with a fun, kid-friendly game featuring capybaras and Roblox-style design!

![Made for Kids](https://img.shields.io/badge/Made%20for-Kids-pink?style=for-the-badge)
![Capybara Approved](https://img.shields.io/badge/🦫-Capybara%20Approved-orange?style=for-the-badge)
![Roblox Style](https://img.shields.io/badge/🎮-Roblox%20Style-blue?style=for-the-badge)

---

## ✨ Features

### 🦫 Capybara & Roblox Theme
- **Kid-friendly design** with capybara emojis everywhere
- **3D blocky buttons** inspired by Roblox
- **Comic Sans font** for a playful feel
- **Bright, colorful gradients** (orange, yellow, green, blue, pink)
- **Playful animations** (wiggle, bounce, float)

### 🎮 Four Game Modes
1. **📚 Übungs-Modus (Practice Mode)** - Learn at your own pace, no timer
2. **⏱️ Zeit-Challenge (Timed Challenge)** - 2 minutes, as many words as possible
3. **🎮 Multiplayer Erstellen (Create Multiplayer)** - Host a game and invite friends
4. **🔗 Multiplayer Beitreten (Join Multiplayer)** - Join a friend's game via session ID

### 🇩🇪 Learn German
- **All 8 German cases**: Nominativ, Genitiv, Dativ, Akkusativ (singular & plural)
- **Real German nouns** from Wiktionary
- **Article practice** with der/die/das
- **All text in German** for immersive learning

### 🌐 Multiplayer Features
- **Session-based multiplayer** with shareable IDs
- **Real-time score tracking**
- **Opponent score display**
- **Winner announcements** in German

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Spin (if not already installed)
curl -fsSL https://developer.fermyon.com/downloads/install.sh | bash

# Add wasm32-wasip1 target
rustup target add wasm32-wasip1
```

### Run the Game
```bash
# Clone repository
git clone https://github.com/avrabe/der-die-das-spin.git
cd der-die-das-spin

# Build and run
cargo build --target wasm32-wasip1 --release
cd der-die-das-spin
spin build
spin up

# Open in browser
open http://localhost:3000
```

### Test Everything
```bash
# After starting spin up, run the verification script
./verify_game.sh
```

See [QUICKSTART.md](./QUICKSTART.md) for more details!

---

## 📦 Download Release

Download the latest release: [Releases](https://github.com/avrabe/der-die-das-spin/releases)

```bash
# Download latest release
wget https://github.com/avrabe/der-die-das-spin/releases/download/v0.1.0/der-die-das-spin-0.1.0.tar.gz

# Extract
tar -xzf der-die-das-spin-0.1.0.tar.gz

# Run
spin up
```

---

## 🛠️ Development

### Project Structure
```
der-die-das-spin/
├── dewiktionary/              # Wiktionary XML parser
├── dewiktionary-diesel/       # Database models and operations
├── dewiktionary-importer-cli/ # CLI tool to import Wiktionary data
├── der-die-das-spin/          # Main Spin application
│   ├── src/lib.rs            # Rust backend with REST API
│   ├── static/               # Frontend files
│   │   ├── index.html        # HTML with Capybara theme
│   │   ├── style.css         # Roblox-style CSS
│   │   └── script.js         # Game logic
│   └── spin.toml             # Spin configuration
├── migrations/                # Database migrations
└── .github/workflows/         # CI/CD pipelines
```

### Build Commands
```bash
# Build all crates
cargo build -p dewiktionary -p dewiktionary-diesel -p dewiktionary-importer-cli --release

# Build WASM module
cargo build --target wasm32-wasip1 --release -p der-die-das

# Build with Spin
cd der-die-das-spin
spin build
```

### Run Tests
```bash
# Run all tests
cargo test --target x86_64-unknown-linux-gnu

# Run API tests
./verify_game.sh
```

### Import Wiktionary Data
```bash
# Download Wiktionary dump
wget https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2

# Import into database
DATABASE_URL=der-die-das-spin/.spin/sqlite_db.db \
  cargo run -p dewiktionary-importer-cli --release -- \
  -f dewiktionary-latest-pages-articles-multistream.xml.bz2
```

---

## 🧪 Testing

See [TESTING.md](./TESTING.md) for comprehensive testing guide with curl examples.

Quick test:
```bash
# Start server
spin up

# In another terminal, test API
curl http://localhost:3000/api/entry.json

# Run full verification
./verify_game.sh
```

---

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Fast start guide for parents and kids
- **[TESTING.md](./TESTING.md)** - Complete API testing guide with curl examples
- **[CAPYBARA_THEME.md](./CAPYBARA_THEME.md)** - Kid-friendly theme documentation
- **[RELEASE.md](./RELEASE.md)** - How to create releases
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history

---

## 🔧 Technical Stack

- **Backend**: Rust + Spin SDK 5.1.1 (WebAssembly)
- **Database**: SQLite with Diesel ORM
- **Parser**: nom-based Wiktionary XML parser
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: Fermyon Spin (serverless WebAssembly)
- **CI/CD**: GitHub Actions
- **Testing**: Tarpaulin (code coverage), cargo-deny (security)

---

## 🚀 Creating a Release

See [RELEASE.md](./RELEASE.md) for detailed release process.

Quick release:
```bash
# 1. Update version in Cargo.toml
vim der-die-das-spin/Cargo.toml

# 2. Update CHANGELOG.md
vim CHANGELOG.md

# 3. Commit and tag
git commit -am "chore: Bump version to 0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main --tags

# 4. GitHub Actions will automatically build and create the release!
```

Or create a release via GitHub UI - the workflow will handle everything!

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/awesome`)
3. Commit changes (`git commit -am 'Add awesome feature'`)
4. Push to branch (`git push origin feature/awesome`)
5. Open a Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Wiktionary** - German noun data
- **Fermyon Spin** - Serverless WebAssembly platform
- **Diesel** - Rust ORM
- **Kids everywhere** who love capybaras and Roblox! 🦫🎮

---

## 💖 Made with Love

Made with 💖 for kids learning German with capybaras and Roblox!

**Viel Spaß beim Deutsch Lernen!** 🦫✨

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/avrabe/der-die-das-spin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/avrabe/der-die-das-spin/discussions)

---

## 🎯 Roadmap

- [ ] More game modes (memory game, speed challenge)
- [ ] Sound effects and background music
- [ ] Progress tracking and achievements
- [ ] More capybara animations
- [ ] Mobile app version
- [ ] Multiplayer tournaments

---

**Have fun learning German! 🦫 Viel Erfolg!**
