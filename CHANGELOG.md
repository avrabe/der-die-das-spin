# Changelog

All notable changes to the Der Die Das Capybara Game will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-11-11

### Added
- 🤖 **Example Sentence Feature** - NEW!
  - "🦫 Beispiel Satz" button on game screen
  - Generates contextual German example sentences for each word
  - Smart sentence generation that never reveals der/die/das
  - Key-value caching for instant responses on repeated words
  - Beautiful animated speech bubble display
  - Loading animation with wiggling capybara
  - Multiple sentence variations per word (5 cached per word)
  - Works with all 4 game modes
- Automated release workflow via GitHub Actions
- Comprehensive release documentation (RELEASE.md)
- Verification script for local testing (verify_game.sh)
- Quick start guide (QUICKSTART.md)
- Capybara & Roblox themed documentation (CAPYBARA_THEME.md)
- Spin features research documentation (SPIN_FEATURES_RESEARCH.md)
- AI implementation plan (IMPLEMENTATION_PLAN_AI_SENTENCES.md)

### Technical
- Added sentence generation module with curated German templates
- Implemented key-value storage for sentence caching
- New REST API endpoint: GET /api/sentence/:word
- Comprehensive test coverage for sentence generation
- Zero clippy warnings
- All tests passing

### Changed
- Release artifacts now include checksums and complete tarball
- Updated spin.toml to enable key_value_stores
- Enhanced frontend with example sentence UI
- Improved educational value through contextual learning

## [0.1.0] - 2025-11-11

### Added
- 🦫 **Complete Capybara & Roblox themed UI**
  - Comic Sans MS font for kid-friendly feel
  - 3D blocky buttons with Roblox-style shadows
  - Capybara emojis throughout the interface
  - Bright gradient backgrounds (orange, yellow, green)
  - Floating capybara decorations
  - Playful animations (wiggle, bounce, float)

- 🎮 **Four Game Modes**
  - Practice Mode: Learn at your own pace, no time limit
  - Timed Challenge: 2-minute countdown with score tracking
  - Multiplayer Create: Host a game and share session ID
  - Multiplayer Join: Join a friend's game via session ID

- 🇩🇪 **Comprehensive German Learning**
  - All 8 German cases (Nominativ, Genitiv, Dativ, Akkusativ × singular/plural)
  - Learn der/die/das articles with real German nouns
  - Complete Wiktionary data extraction
  - German UI text for immersive learning

- 🌐 **Multiplayer Features**
  - UUID-based temporary session management
  - Real-time score tracking
  - Session sharing via copyable session IDs
  - Opponent score display
  - Winner/loser announcements in German

- 🏗️ **Technical Foundation**
  - Upgraded to Spin SDK 5.1.1 (latest)
  - WebAssembly (wasm32-wasip1) for serverless deployment
  - SQLite database for words and sessions
  - REST API for multiplayer coordination
  - Router-based endpoint handling

- ✅ **Quality Assurance**
  - Comprehensive CI/CD pipeline on GitHub Actions
  - Zero cargo warnings
  - Test coverage with Tarpaulin
  - cargo-deny for dependency security
  - Multi-platform testing (Ubuntu, macOS)
  - Automated code coverage reports to Codecov

- 📚 **Documentation**
  - TESTING.md: Complete API testing guide with curl examples
  - CAPYBARA_THEME.md: Kid-friendly theme documentation
  - QUICKSTART.md: Easy start guide for parents and kids
  - README.md: Technical documentation

- 🎨 **Design Features**
  - Responsive design (works on desktop, tablet, mobile)
  - Colorful heart emojis on article buttons (💙💗💚)
  - Capybara victory/defeat animations
  - 3D depth effects on all UI elements
  - Gradient backgrounds with Roblox-inspired colors

### Technical Details
- **Spin Framework**: Upgraded from 3.0.1 to 5.1.1
- **Database**: SQLite with Diesel ORM
- **Parser**: nom-based Wiktionary XML parser
- **Frontend**: Vanilla JavaScript with screen-based navigation
- **Styling**: Custom CSS with animations and 3D effects
- **API Endpoints**:
  - `GET /api/entry.json` - Random word retrieval
  - `POST /api/session/create` - Create multiplayer session
  - `POST /api/session/join` - Join existing session
  - `GET /api/session/:id` - Get session details
  - `POST /api/session/:id/answer` - Submit answer

### Dependencies
- anyhow 1.x
- serde 1.0.190
- serde_json 1.0
- spin-sdk 5.1
- uuid 1.11 (with v4, serde features)
- diesel 2.1.0 (with sqlite)

### Browser Support
- Modern browsers with ES6+ support
- Mobile browsers (iOS Safari, Chrome)
- Tablet browsers
- Desktop browsers (Chrome, Firefox, Safari, Edge)

---

## Version History

- **0.1.0** (2025-11-11): Initial release with capybara theme 🦫

---

## Links

- [Repository](https://github.com/avrabe/der-die-das-spin)
- [Release Notes](./RELEASE.md)
- [Quick Start Guide](./QUICKSTART.md)
- [Testing Guide](./TESTING.md)
- [Theme Documentation](./CAPYBARA_THEME.md)

---

Made with 💖 for kids who love capybaras and Roblox!
