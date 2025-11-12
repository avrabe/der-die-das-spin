/// Example sentence generation module using Spin Serverless AI
/// Provides contextual German sentences for learning without revealing der/die/das
use serde::{Deserialize, Serialize};
use spin_sdk::llm;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ExampleSentence {
    pub sentence: String,
    pub translation: Option<String>,
}

/// Generate a contextual German sentence using LLM
/// The LLM understands the word meaning and creates appropriate sentences
pub fn generate_sentence_with_llm(word: &str, genus: &str) -> Result<String, String> {
    // Create a prompt that asks the LLM to generate a contextual German sentence
    // Important: We tell it NOT to reveal the article
    let prompt = format!(
        "Du bist ein Deutschlehrer für Kinder. Erstelle einen einfachen deutschen Satz mit dem Wort '{}'.

WICHTIG:
- Benutze das Wort '{}' in einem natürlichen Kontext
- Der Satz soll zeigen, wie das Wort verwendet wird
- Verwende NICHT den Nominativ-Artikel (der/die/das) am Anfang
- Verwende stattdessen andere Formen: dem, den, zur, zum, beim, etc.
- Oder verwende das Wort ohne Artikel: mit {}, für {}, etc.
- Der Satz soll für Kinder verständlich sein (maximal 10 Wörter)
- Erwähne manchmal ein Capybara für Spaß!
- Gib NUR den Satz zurück, keine Erklärungen

Beispiele guter Sätze:
- \"Ein Capybara sitzt beim Baum.\"
- \"Ich gehe zur Schule.\"
- \"Das Kind spielt mit dem Ball.\"

Jetzt erstelle einen Satz mit '{}':",
        word, word, word, word, word
    );

    // Use Spin's LLM inference
    match llm::infer(llm::InferencingModel::Llama2Chat, &prompt) {
        Ok(result) => {
            let sentence = result.text.trim().to_string();

            // Basic validation: ensure sentence doesn't reveal the article
            if sentence.starts_with("Der ") || sentence.starts_with("Die ") || sentence.starts_with("Das ") {
                // Fallback to a safe template if LLM reveals the article
                return Ok(generate_fallback_sentence(word, genus));
            }

            // Ensure the sentence contains the word
            if !sentence.contains(word) {
                return Ok(generate_fallback_sentence(word, genus));
            }

            Ok(sentence)
        }
        Err(e) => {
            // If LLM fails, fall back to template-based generation
            eprintln!("LLM inference failed: {:?}, using fallback", e);
            Ok(generate_fallback_sentence(word, genus))
        }
    }
}

/// Fallback sentence generation using simple templates
/// Used when LLM is unavailable or returns invalid results
fn generate_fallback_sentence(word: &str, genus: &str) -> String {
    match genus {
        "m" => format!("Ein Capybara sitzt neben dem {}.", word),
        "f" => format!("Ein Capybara springt über die {}.", word),
        "n" => format!("Ein Capybara steht neben dem {}.", word),
        _ => format!("Capybaras lieben {}!", word),
    }
}

/// Get multiple sentence variations for a word using LLM
pub fn generate_sentences(word: &str, genus: &str, count: usize) -> Vec<ExampleSentence> {
    let mut sentences = Vec::new();

    for _ in 0..count {
        match generate_sentence_with_llm(word, genus) {
            Ok(sentence) => {
                sentences.push(ExampleSentence {
                    sentence,
                    translation: None,
                });
            }
            Err(_) => {
                // Use fallback on error
                sentences.push(ExampleSentence {
                    sentence: generate_fallback_sentence(word, genus),
                    translation: None,
                });
            }
        }
    }

    sentences
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fallback_sentence_masculine() {
        let sentence = generate_fallback_sentence("Tisch", "m");
        assert!(sentence.contains("Tisch"));
        assert!(!sentence.starts_with("Der Tisch"));
    }

    #[test]
    fn test_fallback_sentence_feminine() {
        let sentence = generate_fallback_sentence("Katze", "f");
        assert!(sentence.contains("Katze"));
        assert!(!sentence.starts_with("Die Katze"));
    }

    #[test]
    fn test_fallback_sentence_neuter() {
        let sentence = generate_fallback_sentence("Haus", "n");
        assert!(sentence.contains("Haus"));
        assert!(!sentence.starts_with("Das Haus"));
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
    fn test_no_article_revelation_in_fallback() {
        let words = vec![
            ("Tisch", "m"),
            ("Katze", "f"),
            ("Haus", "n"),
            ("Baum", "m"),
            ("Blume", "f"),
        ];

        for (word, genus) in words {
            let sentence = generate_fallback_sentence(word, genus);
            // None of these patterns should appear at the start
            assert!(!sentence.starts_with(&format!("Der {}", word)));
            assert!(!sentence.starts_with(&format!("Die {}", word)));
            assert!(!sentence.starts_with(&format!("Das {}", word)));
        }
    }
}
