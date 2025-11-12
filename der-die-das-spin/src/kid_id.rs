/// Kid-friendly short ID generation for multiplayer sessions
///
/// Multiple formats available for easy sharing between kids:
/// 1. Animal codes (e.g., "KATZE-42" or "HUND-7")
/// 2. 4-digit numbers (e.g., "1234")
/// 3. 4-6 letter words (e.g., "BAUM", "SONNE")
/// 4. Mixed format (e.g., "K4PY" - letters + numbers)

use rand::{Rng, thread_rng};
use rand::seq::SliceRandom;

/// German animal names - fun and easy for kids to remember
const ANIMALS: &[&str] = &[
    "KATZE", "HUND", "BAER", "FUCHS", "HASE",
    "VOGEL", "FISCH", "MAUS", "PFERD", "KUH",
    "ZIEGE", "SCHAF", "ENTE", "HUHN", "EULE",
    "IGEL", "FROSCH", "BIENE", "WOLF", "ELCH"
];

/// Simple German words - easy to spell
const WORDS: &[&str] = &[
    "BAUM", "HAUS", "BLAU", "GELB", "GRUEN",
    "SONNE", "MOND", "STERN", "BERG", "MEER",
    "BALL", "BUCH", "LIED", "SPIEL", "PARK"
];

/// Generate a 4-digit code (easiest for young kids)
/// Format: "1234" (range: 1000-9999)
pub fn generate_simple_number() -> String {
    let mut rng = thread_rng();
    let num = rng.gen_range(1000..=9999);
    format!("{}", num)
}

/// Generate animal + number code
/// Format: "KATZE-42" or "HUND-7"
/// Perfect for kids: memorable animal + short number
pub fn generate_animal_code() -> String {
    let mut rng = thread_rng();
    let animal = ANIMALS.choose(&mut rng).unwrap();
    let num = rng.gen_range(1..=99);
    format!("{}-{}", animal, num)
}

/// Generate a simple word code
/// Format: "BAUM" or "SONNE"
/// Easy to spell and remember
pub fn generate_word_code() -> String {
    let mut rng = thread_rng();
    WORDS.choose(&mut rng).unwrap().to_string()
}

/// Generate a 6-character mixed alphanumeric code
/// Format: "K4PY8A" (alternating letters and numbers for clarity)
/// Avoids confusing characters: 0/O, 1/I/l
pub fn generate_mixed_code() -> String {
    let mut rng = thread_rng();
    const CLEAR_LETTERS: &[char] = &['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
    const CLEAR_NUMBERS: &[char] = &['2', '3', '4', '5', '6', '7', '8', '9'];

    let mut code = String::with_capacity(6);
    for i in 0..6 {
        if i % 2 == 0 {
            // Even positions: letters
            code.push(*CLEAR_LETTERS.choose(&mut rng).unwrap());
        } else {
            // Odd positions: numbers
            code.push(*CLEAR_NUMBERS.choose(&mut rng).unwrap());
        }
    }
    code
}

/// Generate capybara-themed code (fun for the game!)
/// Format: "CAPY-123"
pub fn generate_capybara_code() -> String {
    let mut rng = thread_rng();
    let num = rng.gen_range(100..=999);
    format!("CAPY-{}", num)
}

/// Recommended: Generate the default kid-friendly ID
/// Uses animal codes as they're most memorable for kids
pub fn generate_default() -> String {
    generate_animal_code()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_number() {
        let id = generate_simple_number();
        assert_eq!(id.len(), 4);
        let num: u32 = id.parse().unwrap();
        assert!(num >= 1000 && num <= 9999);
    }

    #[test]
    fn test_animal_code() {
        let id = generate_animal_code();
        assert!(id.contains('-'));
        let parts: Vec<&str> = id.split('-').collect();
        assert_eq!(parts.len(), 2);
        assert!(ANIMALS.contains(&parts[0]));
    }

    #[test]
    fn test_word_code() {
        let id = generate_word_code();
        assert!(WORDS.contains(&id.as_str()));
    }

    #[test]
    fn test_mixed_code() {
        let id = generate_mixed_code();
        assert_eq!(id.len(), 6);
        // Should not contain confusing characters
        assert!(!id.contains('0'));
        assert!(!id.contains('O'));
        assert!(!id.contains('1'));
        assert!(!id.contains('I'));
    }

    #[test]
    fn test_capybara_code() {
        let id = generate_capybara_code();
        assert!(id.starts_with("CAPY-"));
        let num_part = id.strip_prefix("CAPY-").unwrap();
        let num: u32 = num_part.parse().unwrap();
        assert!(num >= 100 && num <= 999);
    }

    #[test]
    fn test_uniqueness() {
        let mut ids = std::collections::HashSet::new();
        for _ in 0..100 {
            ids.insert(generate_default());
        }
        // Should generate many unique IDs
        assert!(ids.len() > 50);
    }
}
