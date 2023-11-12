fn main() {
    let ddd_spin_dir = "der-die-das-spin";
    //println!("cargo:rerun-if-changed={}", ddd_spin_dir);

    let profile = std::env::var("PROFILE").unwrap();
    let status = std::process::Command::new("cargo")
        .arg("build")
        .arg(format!("--{}", profile))
        .current_dir(ddd_spin_dir)
        .status()
        .expect("failed to execute cargo");

    assert!(status.success(), "failed to build {}", ddd_spin_dir);
}