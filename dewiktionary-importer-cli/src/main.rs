use clap::{crate_version, Parser};
use dewiktionary::parser::DeutschSubstantivUebersicht;
use dewiktionary_diesel::{create_entry, establish_connection};
use diesel::sqlite::SqliteConnection;
use dotenvy::dotenv;
use tracing::{error, info};
use tracing_subscriber::FmtSubscriber;

extern crate bzip2;
extern crate parse_mediawiki_dump_reboot;

/// Options for the application.
#[derive(Parser)]
#[clap(version = crate_version!(), author = "Ralf Anton Beier")]
struct Opts {
    /// The path to the neo4j repository.
    #[clap(
        short,
        long,
        default_value = "dewiktionary-latest-pages-articles-multistream.xml.bz2"
    )]
    filename: String,

    /// The path to the neo4j repository.
    #[clap(short, long, env = "DATABASE_URL")]
    database_url: String,
}

fn main() {
    let subscriber = FmtSubscriber::builder()
        // all spans/events with a level higher than TRACE (e.g, debug, info, warn, etc.)
        // will be written to stdout.
        .with_max_level(tracing::Level::TRACE)
        .with_file(false)
        // completes the builder.
        .finish();

    tracing::subscriber::set_global_default(subscriber).expect("setting default subscriber failed");
    dotenv().ok();
    let opts: Opts = Opts::parse();
    info!("Starting dewiktionary-importer-cli {}", crate_version!());
    info!("Using file {}", opts.filename);

    let file = match std::fs::File::open(&opts.filename) {
        Err(error) => {
            error!("Failed to open input file: {}", error);
            std::process::exit(1);
        }
        Ok(file) => std::io::BufReader::new(file),
    };
    let connection = &mut establish_connection(&opts.database_url);
    if opts.filename.ends_with(".bz2") {
        parse(
            std::io::BufReader::new(bzip2::bufread::MultiBzDecoder::new(file)),
            connection,
        );
    } else {
        parse(file, connection);
    }
}

fn parse(source: impl std::io::BufRead, connection: &mut SqliteConnection) {
    let _ = connection;
    let mut counter = 0;
    let mut gefundene_tabelle = 0;
    for result in parse_mediawiki_dump_reboot::parse(source) {
        match result {
            Err(error) => {
                error!("Error: {}", error);
                std::process::exit(1);
            }
            Ok(page) => {
                counter += 1;
                //if page.title.contains("Kopf") {
                info!(
                    "Tabellen {} von {} Seiten. Aktuell: {}",
                    gefundene_tabelle, counter, page.title
                );
                let tabelle = DeutschSubstantivUebersicht::new(&page.text);
                match tabelle {
                    Some(t) => {
                        info!("Substantivtabelle gefunden");
                        info!("{:#?}", t);
                        gefundene_tabelle += 1;
                        create_entry(
                            connection,
                            &t.nominativ_singular.text,
                            &t.genus.genus,
                            Some(&t.nominativ_plural.text),
                            Some(&t.genitiv_singular.text),
                            Some(&t.genitiv_plural.text),
                            Some(&t.dativ_singular.text),
                            Some(&t.dativ_plural.text),
                            Some(&t.akkusativ_singular.text),
                            Some(&t.akkusativ_plural.text),
                        );
                    }
                    None => {
                        //warn!("Keine Substantivtabelle gefunden");
                        //for line in page.text.lines() {
                        //    info!("{:#?}", line);
                        //}
                    }
                }
                //}
            }
        }
    }
}

// Page {
//     format: Some(
//         "text/x-wiki",
//     ),
//     model: Some(
//         "wikitext",
//     ),
//     namespace: Main,
//     text: "== Kopfnuss ({{Sprache|Deutsch}}) ==\n
//            === {{Wortart|Substantiv|Deutsch}}, {{f}} ===\n\n
//                {{Deutsch Substantiv Übersicht\n|Genus=f\n|Nominativ Singular=Kopfnuss\n|Nominativ Plural=Kopfnüsse\n|Genitiv Singular=Kopfnuss\n|Genitiv Plural=Kopfnüsse\n|Dativ Singular=Kopfnuss\n|Dativ Plural=Kopfnüssen\n|Akkusativ Singular=Kopfnuss\n|Akkusativ Plural=Kopfnüsse\n}}\n\n{{Nicht mehr gültige Schreibweisen}}\n:[[Kopfnuß]]\n\n{{Worttrennung}}\n:Kopf·nuss, {{Pl.}} Kopf·nüs·se\n\n{{Aussprache}}\n:{{IPA}} {{Lautschrift|ˈkɔp\u{361}fˌnʊs}}\n:{{Hörbeispiele}} {{Audio|De-Kopfnuss.ogg}}\n\n{{Bedeutungen}}\n:[1] ein [[leicht]]er [[Schlag]] mit den [[Fingerknöchel]]n auf den [[Kopf]]\n:[2] eine [[Denksportaufgabe]]\n\n{{Herkunft}}\n:[[Determinativkompositum]] ([[Zusammensetzung]]) aus den [[Substantiv]]en ''[[Kopf]]'' und ''[[Nuss]]''\n\n{{Synonyme}}\n:[1] [[Katzenkopf]]\n\n{{Sinnverwandte Wörter}}\n:[1] [[Ohrfeige]]\n\n{{Beispiele}}\n:[1] Er gab mir eine ''Kopfnuss.''\n:[1] Im 19. Jahrhundert war es in Deutschland normal, dass Lehrer geschlagen oder ''Kopfnüsse'' verteilt haben.\n:[1] „»Herr Lehrer, als ich gestern Abend nach Hause kam, stritten sich unsere beiden Kinder. Meine Frau meckerte die beiden an, und ich hab dann auch noch rumgebrüllt, hab der einen sogar eine kleine ''Kopfnuss'' verpasst. Das hätte nicht passieren sollen, ich weiß.«“<ref>{{Per-Deutschlandradio | Online=https://www.deutschlandfunk.de/nachhilfe-fuer-vaeter.795.de.html?dram:article_id=116791 | Autor=Gunnar Köhne | Titel=Nachhilfe für Väter | TitelErg=Rollenbild in der Türkei im Wandel | Tag=27 | Monat=03 | Jahr=2007 | Zugriff=2019-01-08 | Kommentar=Deutschlandradio / Köln, Sendereihe: Europa heute }}</ref>\n:[1] „Es gab in Deutschland eine Zeit, da mussten alle an einem Tisch sitzen, wenn der Vater nach Hause kam, und schön langsam und brav essen, und man musste aufessen. Hat man das nicht getan, hat man eine Watschen oder eine ''Kopfnuss'' bekommen.“<ref>{{Per-Bayerischer Rundfunk | Online=https://www.br.de/fernsehen/ard-alpha/sendungen/alpha-forum/alexander-herrmann-sendung100.html | Autor= | Titel=Sternekoch – Herrmann, Alexander | TitelErg= | Tag=02 | Monat=08 | Jahr=2011 | Zugriff=2019-01-08 | Kommentar= }}</ref>\n:[1] Was das bedeutet, Ärger [im Alltag mit Kunden], das erklärt ihr Kollege Slobodan Trifkovic: „Ob’s körperlich ist, bespucken, oder …“ – „Beißen… Ja, beißen, oder ob man sich eine ''Kopfnuss'' einfängt.“<ref>{{Per-Deutschlandradio | Online=https://www.deutschlandfunk.de/angriffe-auf-behoerdenmitarbeiter-vorfaelle-werden-oft.1769.de.html?dram:article_id=350221 | Autor=Vivien Leue | Titel=Angriffe auf BehördenmitarbeiterVorfälle werden oft bagatellisiert | TitelErg= | Tag=04 | Monat=04 | Jahr=2016 | Zugriff=2019-01-08 | Kommentar=Detschlandfunk / Köln, Sendereihe: Deutschland heute }}</ref>\n:[2] Dieses Rätsel war schon eine ''Kopfnuss.'' \n\n==== {{Übersetzungen}} ====\n{{Ü-Tabelle|1|G=ein [[leicht]]er [[Schlag]] mit den [[Fingerknöchel]]n auf den [[Kopf]]|Ü-Liste=\n*{{en}}: {{Ü|en|}}\n*{{fr}}: [1] {{Ü|fr|tape sur la tête}} {{f}}; [2] {{Ü|fr|casse-tête}} {{m}}\n*{{sv}}: {{Ü|sv|tankenöt}}\n}}\n{{Ü-Tabelle|2|G=eine [[Denksportaufgabe]]|Ü-Liste=\n*{{en}}: {{Ü|en|brain teaser}}<ref>{{Wikipedia|Brain teaser|brain teaser|spr=en}}</ref>\n*{{sv}}: {{Ü|sv|}}\n}}\n\n{{Referenzen}}\n:[1, 2] {{Wikipedia|Kopfnuss}}\n:[1] {{Ref-DWDS|Kopfnuß}}\n:[*] {{Ref-UniLeipzig|Kopfnuss}}\n:[*] {{Ref-OWID|elexiko|210954|Kopfnuss}}\n:[1, 2] {{Ref-Pons|Kopfnuß}}\n:[1, 2] {{Ref-FreeDictionary|Kopfnuss}}\n:[1] Deutsche Welle, Deutsch lernen – Wort der Woche: {{Per-Deutsche Welle | Online=https://p.dw.com/p/18KnN | Autor=Hanna Grimm | Titel=Die Kopfnuss | TitelErg= | Tag=24 | Monat=06 | Jahr=2013 | Zugriff=2019-01-05 | Kommentar=Text und [https://www.dw.com/overlay/media/de/die-kopfnuss/16737550/16762901 Audio zum Download], Dauer 01:25 mm:ss }}\n\n{{Quellen}}\n\n{{Ähnlichkeiten 1|[[Kopfschuss]]}}",
//     title: "Kopfnuss",
// }
