use nom::bytes::complete::tag;
use nom::character::complete::{alpha1, anychar, multispace0};
use nom::combinator::{map, recognize};

use nom::multi::many_till;
use nom::sequence::{delimited, preceded, tuple};
use nom::IResult;

#[derive(PartialEq, Eq, Debug)]
pub struct Genus {
    pub genus: String,
}
impl Genus {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let b = preceded(tag("Genus"), a);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            genus: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct NominativSingular {
    pub text: String,
}

impl NominativSingular {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Singular"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Nominativ"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct NominativPlural {
    pub text: String,
}
impl NominativPlural {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Plural"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Nominativ"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct GenitivSingular {
    pub text: String,
}
impl GenitivSingular {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Singular"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Genitiv"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct GenitivPlural {
    pub text: String,
}
impl GenitivPlural {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Plural"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Genitiv"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct DativSingular {
    pub text: String,
}
impl DativSingular {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Singular"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Dativ"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct DativPlural {
    pub text: String,
}
impl DativPlural {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Plural"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Dativ"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct AkkusativSingular {
    pub text: String,
}
impl AkkusativSingular {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Singular"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Akkusativ"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]
pub struct AkkusativPlural {
    pub text: String,
}
impl AkkusativPlural {
    fn parse(input: &str) -> IResult<&str, Self> {
        let a = preceded(tag("="), alpha1);
        let a1 = preceded(tag("Plural"), a);
        let a2 = preceded(multispace0, a1);

        let b = preceded(tag("Akkusativ"), a2);
        let c = preceded(tag("|"), b);
        let d = preceded(multispace0, c);

        let mut my_parser = map(d, |rest: &str| Self {
            text: rest.to_string(),
        });

        my_parser(input)
    }
}

#[derive(PartialEq, Eq, Debug)]

pub struct DeutschSubstantivUebersicht {
    pub genus: Genus,
    pub nominativ_singular: NominativSingular,
    pub nominativ_plural: NominativPlural,
    pub genitiv_singular: GenitivSingular,
    pub genitiv_plural: GenitivPlural,
    pub dativ_singular: DativSingular,
    pub dativ_plural: DativPlural,
    pub akkusativ_singular: AkkusativSingular,
    pub akkusativ_plural: AkkusativPlural,
}

impl DeutschSubstantivUebersicht {
    pub fn new(input: &str) -> Option<Self> {
        let parse_wiktionary_seite = DeutschSubstantivUebersicht::parse(input);
        match parse_wiktionary_seite {
            Ok((_remaining, overview)) => Some(overview),
            Err(_e) => None,
        }
    }

    //{{Deutsch Substantiv Übersicht
    fn parse_until(input: &str) -> IResult<&str, &str> {
        let a = preceded(multispace0, tag("Übersicht"));
        let a1 = preceded(tag("Substantiv"), a);
        let a2 = preceded(multispace0, a1);
        let a3 = preceded(tag("Deutsch"), a2);
        let a4 = preceded(multispace0, a3);
        let a5 = preceded(tag("{{"), a4);
        let mut a6 = preceded(multispace0, a5);
        a6(input)
    }

    // This is a function that uses the custom tag to drop any input until it finds your parser function
    fn drop_until_deutsch(input: &str) -> IResult<&str, &str> {
        let mut recognize_tabelle =
            recognize(many_till(anychar, DeutschSubstantivUebersicht::parse_until));
        recognize_tabelle(input)
        //((let (input, _) = take_until(DeutschSubstantivUebersicht::parse_until)(input)?; // drop the input before your parser function
        //rest(input) // return the rest of the input
    }

    fn parse(input: &str) -> IResult<&str, Self> {
        let b = preceded(multispace0, tag("}}"));

        let c = tuple((
            Genus::parse,
            NominativSingular::parse,
            NominativPlural::parse,
            GenitivSingular::parse,
            GenitivPlural::parse,
            DativSingular::parse,
            DativPlural::parse,
            AkkusativSingular::parse,
            AkkusativPlural::parse,
        ));
        let d = delimited(Self::drop_until_deutsch, c, b);
        let mut my_parser = map(d, |(g, ns, np, gs, gp, ds, dp, a_s, ap)| Self {
            genus: g,
            nominativ_singular: ns,
            nominativ_plural: np,
            genitiv_singular: gs,
            genitiv_plural: gp,
            dativ_singular: ds,
            dativ_plural: dp,
            akkusativ_singular: a_s,
            akkusativ_plural: ap,
        });

        my_parser(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn genus() {
        let foo = Genus::parse("|Genus=f");
        let verify = Ok((
            "",
            Genus {
                genus: String::from("f"),
            },
        ));
        assert_eq!(foo, verify);

        let foo = Genus::parse("  \t\n\r |Genus=f");
        assert_eq!(foo, verify);
    }

    #[test]
    fn nominativ_singular() {
        let foo = NominativSingular::parse("|Nominativ Singular=Kopfschmerztablette");
        let verify = Ok((
            "",
            NominativSingular {
                text: String::from("Kopfschmerztablette"),
            },
        ));
        assert_eq!(foo, verify);

        let foo = NominativSingular::parse("  \t\n\r |Nominativ Singular=Kopfschmerztablette");
        assert_eq!(foo, verify);
    }

    #[test]
    fn ubersicht() {
        let foo = DeutschSubstantivUebersicht::parse(
            "   {{Deutsch Substantiv Übersicht
            |Genus=f
            |Nominativ Singular=Kopfschmerztablette
            |Nominativ Plural=Kopfschmerztabletten
            |Genitiv Singular=Kopfschmerztablette
            |Genitiv Plural=Kopfschmerztabletten
            |Dativ Singular=Kopfschmerztablette
            |Dativ Plural=Kopfschmerztabletten
            |Akkusativ Singular=Kopfschmerztablette
            |Akkusativ Plural=Kopfschmerztabletten
            }}",
        );
        let verify = Ok((
            "",
            DeutschSubstantivUebersicht {
                genus: Genus {
                    genus: "f".to_string(),
                },
                nominativ_singular: NominativSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                nominativ_plural: NominativPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
                genitiv_singular: GenitivSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                genitiv_plural: GenitivPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
                dativ_singular: DativSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                dativ_plural: DativPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
                akkusativ_singular: AkkusativSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                akkusativ_plural: AkkusativPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
            },
        ));
        assert_eq!(foo, verify);
    }

    #[test]
    fn alles() {
        let foo = DeutschSubstantivUebersicht::parse(
            "abcde ds fdjfdsl flkdsj  {{Deutsch Substantiv Übersicht
            |Genus=f
            |Nominativ Singular=Kopfschmerztablette
            |Nominativ Plural=Kopfschmerztabletten
            |Genitiv Singular=Kopfschmerztablette
            |Genitiv Plural=Kopfschmerztabletten
            |Dativ Singular=Kopfschmerztablette
            |Dativ Plural=Kopfschmerztabletten
            |Akkusativ Singular=Kopfschmerztablette
            |Akkusativ Plural=Kopfschmerztabletten
            }}",
        );
        let verify = Ok((
            "",
            DeutschSubstantivUebersicht {
                genus: Genus {
                    genus: "f".to_string(),
                },
                nominativ_singular: NominativSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                nominativ_plural: NominativPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
                genitiv_singular: GenitivSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                genitiv_plural: GenitivPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
                dativ_singular: DativSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                dativ_plural: DativPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
                akkusativ_singular: AkkusativSingular {
                    text: "Kopfschmerztablette".to_string(),
                },
                akkusativ_plural: AkkusativPlural {
                    text: "Kopfschmerztabletten".to_string(),
                },
            },
        ));
        assert_eq!(foo, verify);
    }
}

/*
=== {{Wortart|Substantiv|Deutsch}}, {{f}} ===

{{Deutsch Substantiv Übersicht
|Genus=f
|Nominativ Singular=Kopfschmerztablette
|Nominativ Plural=Kopfschmerztabletten
|Genitiv Singular=Kopfschmerztablette
|Genitiv Plural=Kopfschmerztabletten
|Dativ Singular=Kopfschmerztablette
|Dativ Plural=Kopfschmerztabletten
|Akkusativ Singular=Kopfschmerztablette
|Akkusativ Plural=Kopfschmerztabletten
}}
*/
