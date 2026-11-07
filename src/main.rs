#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use mini_game_core::{compute_highscore_signature, synthesize_stereo_tone_wav};
use std::path::{Path, PathBuf};
use std::process::Command;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|a| a == "--version" || a == "-V") {
        println!("Mini Game Sammlung v1.3.0 (Native Rust Core & Launcher)");
        return;
    }
    if args.iter().any(|a| a == "--verify") {
        let wav = synthesize_stereo_tone_wav(440.0, 120, 0.8, 0.0, 0);
        let sig = compute_highscore_signature(&wav);
        println!(
            "Rust Audio & Integrity Core OK (WAV bytes: {}, FNV-1a: {:016x})",
            wav.len(),
            sig
        );
        return;
    }

    let exe_path = std::env::current_exe().unwrap_or_else(|_| PathBuf::from("."));
    let base_dir = exe_path.parent().unwrap_or_else(|| Path::new(".")).to_path_buf();
    let main_py = base_dir.join("main.py");

    if main_py.is_file() {
        let _ = Command::new("pythonw")
            .arg(&main_py)
            .current_dir(&base_dir)
            .spawn()
            .or_else(|_| {
                Command::new("python")
                    .arg(&main_py)
                    .current_dir(&base_dir)
                    .spawn()
            });
    }
}
