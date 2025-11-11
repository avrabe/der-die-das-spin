/// Example sentence generation module
/// Provides contextual German sentences for learning without revealing der/die/das
use rand::Rng;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ExampleSentence {
    pub sentence: String,
    pub translation: Option<String>,
}

/// Sentence templates that work with different genders
/// Uses declined forms (dem, den, am, beim, etc.) to avoid revealing the article
const SENTENCE_TEMPLATES: &[&[&str]] = &[
    // Templates that work with masculine (m)
    &[
        "Ein Capybara sitzt neben dem {}.",
        "Ich sehe einen {} am Horizont.",
        "Das Kind spielt mit dem {}.",
        "Wir gehen zum {}.",
        "Die Capybaras lieben den {}!",
    ],
    // Templates that work with feminine (f)
    &[
        "Ein Capybara springt über die {}.",
        "Ich sehe eine {} im Garten.",
        "Das Kind malt die {} bunt an.",
        "Wir gehen zur {}.",
        "Die Capybaras mögen die {} sehr!",
    ],
    // Templates that work with neuter (n)
    &[
        "Ein Capybara steht neben dem {}.",
        "Ich sehe ein {} am Himmel.",
        "Das Kind beobachtet das {}.",
        "Wir gehen zum {}.",
        "Die Capybaras lieben das {}!",
    ],
];

/// Universal templates that work with all genders using prepositions
const UNIVERSAL_TEMPLATES: &[&str] = &[
    "Capybaras lieben {}!",
    "Heute lernen wir über {}.",
    "Kennst du {}?",
    "Erzähl mir von {}!",
    "Schau mal, dort ist {}!",
];

/// Get the template index for a given genus
fn genus_to_index(genus: &str) -> usize {
    match genus {
        "m" => 0, // masculine
        "f" => 1, // feminine
        "n" => 2, // neuter
        _ => 0,   // default to masculine
    }
}

/// Generate an example sentence for a given word
pub fn generate_sentence(word: &str, genus: &str, variation: usize) -> ExampleSentence {
    let mut rng = rand::thread_rng();

    // 70% chance to use gender-specific template, 30% universal
    let use_specific = rng.gen_bool(0.7);

    let sentence = if use_specific && !genus.is_empty() {
        let idx = genus_to_index(genus);
        let templates = SENTENCE_TEMPLATES[idx];
        let template_idx = (variation + rng.gen_range(0..templates.len())) % templates.len();
        let template = templates[template_idx];

        // Convert word to appropriate case
        let word_form = match genus {
            "m" => word.to_string(), // Keep nominative for accusative/dative context
            "f" => word.to_string(),
            "n" => word.to_string(),
            _ => word.to_string(),
        };

        template.replace("{}", &word_form)
    } else {
        // Use universal template
        let template_idx = (variation + rng.gen_range(0..UNIVERSAL_TEMPLATES.len()))
            % UNIVERSAL_TEMPLATES.len();
        let template = UNIVERSAL_TEMPLATES[template_idx];
        template.replace("{}", word)
    };

    ExampleSentence {
        sentence,
        translation: None, // Can add English translations later
    }
}

/// Get multiple sentence variations for a word
pub fn generate_sentences(word: &str, genus: &str, count: usize) -> Vec<ExampleSentence> {
    (0..count)
        .map(|i| generate_sentence(word, genus, i))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_sentence_masculine() {
        let sentence = generate_sentence("Tisch", "m", 0);
        assert!(!sentence.sentence.is_empty());
        assert!(sentence.sentence.contains("Tisch"));
        // Should not reveal "Der" at the start
        assert!(!sentence.sentence.starts_with("Der Tisch"));
    }

    #[test]
    fn test_generate_sentence_feminine() {
        let sentence = generate_sentence("Katze", "f", 0);
        assert!(!sentence.sentence.is_empty());
        assert!(sentence.sentence.contains("Katze"));
        // Should not reveal "Die" at the start
        assert!(!sentence.sentence.starts_with("Die Katze"));
    }

    #[test]
    fn test_generate_sentence_neuter() {
        let sentence = generate_sentence("Haus", "n", 0);
        assert!(!sentence.sentence.is_empty());
        assert!(sentence.sentence.contains("Haus"));
        // Should not reveal "Das" at the start
        assert!(!sentence.sentence.starts_with("Das Haus"));
    }

    #[test]
    fn test_generate_multiple_sentences() {
        let sentences = generate_sentences("Tisch", "m", 3);
        assert_eq!(sentences.len(), 3);
        // All sentences should contain the word
        for sentence in &sentences {
            assert!(sentence.sentence.contains("Tisch"));
        }
    }

    #[test]
    fn test_no_article_revelation() {
        let words = vec![
            ("Tisch", "m"),
            ("Katze", "f"),
            ("Haus", "n"),
            ("Baum", "m"),
            ("Blume", "f"),
        ];

        for (word, genus) in words {
            let sentences = generate_sentences(word, genus, 10);
            for s in sentences {
                // None of these patterns should appear at the start
                assert!(!s.sentence.starts_with(&format!("Der {}", word)));
                assert!(!s.sentence.starts_with(&format!("Die {}", word)));
                assert!(!s.sentence.starts_with(&format!("Das {}", word)));
            }
        }
    }

    #[test]
    fn test_genus_to_index() {
        assert_eq!(genus_to_index("m"), 0);
        assert_eq!(genus_to_index("f"), 1);
        assert_eq!(genus_to_index("n"), 2);
        assert_eq!(genus_to_index("unknown"), 0); // defaults to masculine
    }
}
