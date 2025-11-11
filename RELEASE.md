# 🚀 Release Process

This document describes how to create a new release of the Der Die Das Capybara Game.

---

## 📋 Prerequisites

Before creating a release:

1. ✅ All tests pass on main branch
2. ✅ CI/CD pipelines are green
3. ✅ CHANGELOG.md is updated with new version
4. ✅ Version bumped in `der-die-das-spin/Cargo.toml`
5. ✅ All features tested locally with `./verify_game.sh`

---

## 🎯 Release Workflow

The project uses automated GitHub Actions to build and release when you create a new tag.

### Automatic Triggers

The release workflow triggers on:
- **Creating a GitHub Release** via the GitHub UI
- **Pushing a version tag** (e.g., `v0.2.0`)

### What Happens Automatically

When you trigger a release, the CI will:

1. ✅ **Build** all crates (dewiktionary, importer, diesel, WASM module)
2. ✅ **Run tests** to ensure quality
3. ✅ **Create artifacts**:
   - `der-die-das-spin-{version}.tar.gz` - Complete application package
   - `der_die_das.wasm` - WebAssembly module
   - `checksums.txt` - SHA256 checksums
4. ✅ **Upload to GitHub Release** with:
   - Release notes
   - Quick start guide
   - All artifacts
5. ⚙️ **Deploy to Fermyon Cloud** (optional, currently commented out)

---

## 📦 Creating a Release

### Method 1: Via GitHub UI (Recommended)

1. Go to: https://github.com/avrabe/der-die-das-spin/releases
2. Click **"Draft a new release"**
3. Click **"Choose a tag"** → Type new version (e.g., `v0.2.0`) → **"Create new tag"**
4. **Release title**: `v0.2.0 - Capybara Game Update 🦫`
5. **Description**: Add your release notes
6. Click **"Publish release"**
7. ✨ GitHub Actions will automatically build and upload artifacts!

### Method 2: Via Git Command Line

```bash
# 1. Update version in Cargo.toml
vim der-die-das-spin/Cargo.toml
# Change version = "0.1.0" to version = "0.2.0"

# 2. Update CHANGELOG.md
vim CHANGELOG.md

# 3. Commit version bump
git add der-die-das-spin/Cargo.toml CHANGELOG.md
git commit -m "chore: Bump version to 0.2.0"
git push origin main

# 4. Create and push tag
git tag -a v0.2.0 -m "Release v0.2.0 - Capybara Game Update 🦫"
git push origin v0.2.0

# 5. GitHub Actions will automatically create the release!
```

---

## 🏷️ Version Naming

Follow [Semantic Versioning](https://semver.org/):

- **Major** (v1.0.0): Breaking changes, major redesign
- **Minor** (v0.2.0): New features, backwards compatible
- **Patch** (v0.1.1): Bug fixes, small improvements

Examples:
- `v0.1.0` - Initial release
- `v0.2.0` - Added multiplayer mode
- `v0.2.1` - Fixed multiplayer bug
- `v1.0.0` - Stable public release

---

## 📝 Release Notes Template

Use this template for your release notes:

```markdown
## 🦫 Der Die Das - Capybara Game v0.2.0

### ✨ New Features
- Added capybara animations
- Improved Roblox-style UI
- New practice mode

### 🐛 Bug Fixes
- Fixed multiplayer session creation
- Corrected German article handling

### 🔧 Improvements
- Better mobile responsiveness
- Faster word loading

### 📚 Documentation
- Updated QUICKSTART.md
- Added verification script

### 🙏 Thanks
Special thanks to @username for contributions!
```

---

## 🎨 Release Artifacts

Each release includes:

### 1. `der-die-das-spin-{version}.tar.gz`
Complete application package containing:
- `der_die_das.wasm` - The compiled WebAssembly module
- `spin.toml` - Spin configuration
- `static/` - Frontend files (HTML, CSS, JS)

**Usage:**
```bash
tar -xzf der-die-das-spin-0.2.0.tar.gz
spin up
```

### 2. `der_die_das.wasm`
Standalone WebAssembly module for custom deployments.

### 3. `checksums.txt`
SHA256 checksums for verifying downloads:
```bash
sha256sum -c checksums.txt
```

---

## 🌐 Optional: Deploy to Fermyon Cloud

To enable automatic deployment to Fermyon Cloud on release:

1. **Uncomment the deploy job** in `.github/workflows/release.yml`
2. **Add Spin auth token** to GitHub Secrets:
   ```bash
   # Get your token
   spin cloud login

   # Add to GitHub: Settings → Secrets → Actions → New secret
   # Name: SPIN_AUTH_TOKEN
   # Value: <your-token>
   ```
3. **Update spin.toml** with your cloud configuration:
   ```toml
   [application]
   name = "der-die-das"
   [application.trigger.http]
   base = "/"
   ```

Now releases will automatically deploy!

---

## 🧪 Testing Before Release

Always test before releasing:

```bash
# 1. Build locally
cd der-die-das-spin
cargo build --target wasm32-wasip1 --release
spin build

# 2. Start application
spin up

# 3. Run verification script (in another terminal)
./verify_game.sh

# 4. Manual browser testing
open http://localhost:3000

# 5. Test all game modes:
#    - Practice mode
#    - Timed challenge
#    - Multiplayer create/join
```

---

## 🔍 Verifying a Release

After creating a release:

1. **Check GitHub Actions**: Ensure workflow completed successfully
2. **Download artifacts**: Verify they're present on the release page
3. **Test the release**:
   ```bash
   wget https://github.com/avrabe/der-die-das-spin/releases/download/v0.2.0/der-die-das-spin-0.2.0.tar.gz
   tar -xzf der-die-das-spin-0.2.0.tar.gz
   sha256sum -c checksums.txt
   spin up
   ```
4. **Check deployment**: If auto-deploy enabled, verify at your cloud URL

---

## 📊 Release Checklist

Before publishing:

- [ ] Version updated in `der-die-das-spin/Cargo.toml`
- [ ] CHANGELOG.md updated
- [ ] All tests pass locally
- [ ] `./verify_game.sh` passes
- [ ] Browser testing completed (all 4 game modes)
- [ ] Git tag created with correct format (`vX.Y.Z`)
- [ ] Release notes written
- [ ] CI/CD pipeline green

After publishing:

- [ ] GitHub Actions completed successfully
- [ ] All artifacts uploaded to release
- [ ] Checksums verified
- [ ] Release tested by downloading artifacts
- [ ] (Optional) Cloud deployment verified
- [ ] Announcement made (if applicable)

---

## 🐛 Troubleshooting

### Release workflow failed

**Check:**
1. GitHub Actions logs for errors
2. Rust compilation errors
3. Test failures
4. Permissions (workflow needs `contents: write`)

### Artifacts not uploading

**Solutions:**
1. Ensure tag format is correct: `vX.Y.Z`
2. Check `softprops/action-gh-release` permissions
3. Verify `GITHUB_TOKEN` has proper scopes

### Deploy to cloud failed

**Solutions:**
1. Verify `SPIN_AUTH_TOKEN` secret is set
2. Check Spin CLI version compatibility
3. Ensure spin.toml has correct configuration
4. Test `spin cloud deploy` locally first

---

## 🔄 Hotfix Releases

For urgent bug fixes:

```bash
# 1. Create hotfix branch from tag
git checkout -b hotfix/v0.1.1 v0.1.0

# 2. Make fix
vim der-die-das-spin/src/lib.rs
git commit -am "fix: Critical bug in session handling"

# 3. Bump patch version
vim der-die-das-spin/Cargo.toml  # 0.1.0 → 0.1.1

# 4. Merge to main
git checkout main
git merge hotfix/v0.1.1
git push origin main

# 5. Create release tag
git tag -a v0.1.1 -m "Hotfix v0.1.1"
git push origin v0.1.1
```

---

## 📈 Release History

| Version | Date | Highlights |
|---------|------|------------|
| v0.1.0  | 2025-11-11 | Initial release with capybara theme 🦫 |

---

## 🦫 Made with Love

Every release is made with 💖 for kids learning German with capybaras and Roblox!

**Questions?** Open an issue: https://github.com/avrabe/der-die-das-spin/issues
