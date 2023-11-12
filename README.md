# der-die-das-spin

[![Rust](https://github.com/avrabe/der-die-das-spin/actions/workflows/rust-native.yml/badge.svg)](https://github.com/avrabe/der-die-das-spin/actions/workflows/rust-native.yml)
[![codecov](https://codecov.io/gh/avrabe/der-die-das-spin/graph/badge.svg?token=jywfs1sW4p)](https://codecov.io/gh/avrabe/der-die-das-spin)

A simple web app to practice German articles (der, die, das). Select an article and spin the wheel to reveal a random noun.

<https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2>

```sh
# component tools https://github.com/fermyon/spin-fileserver/tree/main/examples/rust
rustup target add wasm32-wasi
cargo install cargo-component
cargo install --locked --git https://github.com/dicej/wasm-tools --branch wasm-compose-resource-imports wasm-tools

cargo install cargo-deny
cargo install diesel_cli --no-default-features --features sqlite
diesel setup
```
