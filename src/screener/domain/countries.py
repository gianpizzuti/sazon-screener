"""Countries that issue driving licences, and the ways candidates name them.

Used only for a licence's country, when the candidate says it is from abroad ("es de Marruecos",
"carnet italiano", "UK licence"). Never to infer nationality: Sofía never asks where a candidate or
their licence is from, and the country only decides what the law of the place they'd work says
(config `foreign_licences.yaml`, D222).
"""

from __future__ import annotations

from screener.domain.text import contains_phrase, normalize

# ISO code: (Spanish name, English name, other ways to write it, accent-free)
COUNTRIES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    # European Union and European Economic Area
    "AT": ("Austria", "Austria", ("austriaco", "austriaca", "austrian")),
    "BE": ("Bélgica", "Belgium", ("belga", "belgian")),
    "BG": ("Bulgaria", "Bulgaria", ("bulgaro", "bulgara", "bulgarian")),
    "HR": ("Croacia", "Croatia", ("croata", "croatian")),
    "CY": ("Chipre", "Cyprus", ("chipriota", "cypriot")),
    "CZ": ("Chequia", "Czechia", ("republica checa", "checo", "checa", "czech republic", "czech")),
    "DK": ("Dinamarca", "Denmark", ("danes", "danesa", "danish")),
    "EE": ("Estonia", "Estonia", ("estonio", "estonian")),
    "FI": ("Finlandia", "Finland", ("finlandes", "finlandesa", "finnish")),
    "FR": ("Francia", "France", ("frances", "francesa", "french")),
    "DE": ("Alemania", "Germany", ("aleman", "alemana", "german")),
    "GR": ("Grecia", "Greece", ("griego", "griega", "greek")),
    "HU": ("Hungría", "Hungary", ("hungaro", "hungara", "hungarian")),
    "IE": ("Irlanda", "Ireland", ("irlandes", "irlandesa", "irish")),
    "IT": ("Italia", "Italy", ("italiano", "italiana", "italian")),
    "LV": ("Letonia", "Latvia", ("leton", "letona", "latvian")),
    "LT": ("Lituania", "Lithuania", ("lituano", "lituana", "lithuanian")),
    "LU": ("Luxemburgo", "Luxembourg", ("luxemburgues", "luxemburguesa")),
    "MT": ("Malta", "Malta", ("maltes", "maltesa", "maltese")),
    "NL": ("Países Bajos", "Netherlands", ("holanda", "holandes", "holandesa", "neerlandes", "neerlandesa", "dutch", "holland")),
    "PL": ("Polonia", "Poland", ("polaco", "polaca", "polish")),
    "PT": ("Portugal", "Portugal", ("portugues", "portuguesa", "portuguese")),
    "RO": ("Rumanía", "Romania", ("rumania", "rumano", "rumana", "romanian")),
    "SK": ("Eslovaquia", "Slovakia", ("eslovaco", "eslovaca", "slovak")),
    "SI": ("Eslovenia", "Slovenia", ("esloveno", "eslovena", "slovenian")),
    "SE": ("Suecia", "Sweden", ("sueco", "sueca", "swedish")),
    "IS": ("Islandia", "Iceland", ("islandes", "islandesa", "icelandic")),
    "LI": ("Liechtenstein", "Liechtenstein", ()),
    "NO": ("Noruega", "Norway", ("noruego", "noruega", "norwegian")),
    "ES": ("España", "Spain", ("espanol", "espanola", "spanish")),
    # Countries with a licence-exchange agreement with Spain (DGT list, 26/06/2026)
    "AD": ("Andorra", "Andorra", ("andorrano", "andorrana")),
    "CH": ("Suiza", "Switzerland", ("suizo", "swiss")),
    "MC": ("Mónaco", "Monaco", ("monegasco", "monegasca")),
    "GB": ("Reino Unido", "United Kingdom", ("uk", "gran bretana", "inglaterra", "escocia", "gales", "ingles", "inglesa",
                                            "britanico", "britanica", "british", "english", "england", "great britain")),
    "MA": ("Marruecos", "Morocco", ("marroqui", "moroccan")),
    "DZ": ("Argelia", "Algeria", ("argelino", "argelina", "algerian")),
    "TN": ("Túnez", "Tunisia", ("tunecino", "tunecina", "tunisian")),
    "TR": ("Turquía", "Turkey", ("turco", "turca", "turkish", "turkiye")),
    "UA": ("Ucrania", "Ukraine", ("ucraniano", "ucraniana", "ukrainian")),
    "MD": ("Moldavia", "Moldova", ("moldavo", "moldava", "moldovan")),
    "RS": ("Serbia", "Serbia", ("serbio", "serbian")),
    "MK": ("Macedonia del Norte", "North Macedonia", ("macedonia", "macedonio", "macedonian")),
    "GE": ("Georgia", "Georgia", ("georgiano", "georgiana", "georgian")),
    "JP": ("Japón", "Japan", ("japones", "japonesa", "japanese")),
    "KR": ("Corea del Sur", "South Korea", ("corea", "coreano", "coreana", "korean", "korea")),
    "PH": ("Filipinas", "Philippines", ("filipino", "filipina", "philippine")),
    "NZ": ("Nueva Zelanda", "New Zealand", ("neozelandes", "neozelandesa")),
    "AR": ("Argentina", "Argentina", ("argentino", "argentinian", "argentine")),
    "BO": ("Bolivia", "Bolivia", ("boliviano", "boliviana", "bolivian")),
    "BR": ("Brasil", "Brazil", ("brasileno", "brasilena", "brazilian")),
    "CL": ("Chile", "Chile", ("chileno", "chilena", "chilean")),
    "CO": ("Colombia", "Colombia", ("colombiano", "colombiana", "colombian")),
    "CR": ("Costa Rica", "Costa Rica", ("costarricense", "costa rican")),
    "EC": ("Ecuador", "Ecuador", ("ecuatoriano", "ecuatoriana", "ecuadorian")),
    "SV": ("El Salvador", "El Salvador", ("salvadoreno", "salvadorena", "salvadoran")),
    "GT": ("Guatemala", "Guatemala", ("guatemalteco", "guatemalteca", "guatemalan")),
    "HN": ("Honduras", "Honduras", ("hondureno", "hondurena", "honduran")),
    "NI": ("Nicaragua", "Nicaragua", ("nicaraguense", "nicaraguan")),
    "PA": ("Panamá", "Panama", ("panameno", "panamena", "panamanian")),
    "PY": ("Paraguay", "Paraguay", ("paraguayo", "paraguaya", "paraguayan")),
    "PE": ("Perú", "Peru", ("peruano", "peruana", "peruvian")),
    "DO": ("República Dominicana", "Dominican Republic", ("dominicano", "dominicana", "dominican")),
    "UY": ("Uruguay", "Uruguay", ("uruguayo", "uruguaya", "uruguayan")),
    # Frequent countries of origin without an agreement with Spain
    "VE": ("Venezuela", "Venezuela", ("venezolano", "venezolana", "venezuelan")),
    "MX": ("México", "Mexico", ("mexicano", "mexicana", "mexican")),
    "US": ("Estados Unidos", "United States", ("eeuu", "ee uu", "usa", "us", "estadounidense", "americano", "americana",
                                               "american", "united states of america")),
    "CA": ("Canadá", "Canada", ("canadiense", "canadian")),
    "CU": ("Cuba", "Cuba", ("cubano", "cubana", "cuban")),
    "AU": ("Australia", "Australia", ("australiano", "australiana", "australian")),
    "CN": ("China", "China", ("chino", "chinese")),
    "IN": ("India", "India", ("indio", "indian")),
    "PK": ("Pakistán", "Pakistan", ("pakistani",)),
    "BD": ("Bangladés", "Bangladesh", ("bangladesh", "bangladesi")),
    "SN": ("Senegal", "Senegal", ("senegales", "senegalesa", "senegalese")),
    "NG": ("Nigeria", "Nigeria", ("nigeriano", "nigeriana", "nigerian")),
    "GH": ("Ghana", "Ghana", ("ghanes", "ghanesa", "ghanaian")),
    "ML": ("Malí", "Mali", ("maliense", "malian")),
    "RU": ("Rusia", "Russia", ("ruso", "rusa", "russian")),
    "GQ": ("Guinea Ecuatorial", "Equatorial Guinea", ("ecuatoguineano", "ecuatoguineana")),
}

# Longest first, so "guinea ecuatorial" wins over a shorter name inside it
_ALIASES = sorted(
    {(normalize(alias), code) for code, (es, en, more) in COUNTRIES.items() for alias in (es, en, *more)},
    key=lambda pair: -len(pair[0]),
)


def country_code(text: str | None) -> str | None:
    """'es de Marruecos' -> 'MA', 'italiana' -> 'IT'; None if no known country is named."""
    norm = normalize(text or "")
    return next((code for alias, code in _ALIASES if contains_phrase(norm, alias)), None)


def country_name(value: str | None, locale: str = "es") -> str:
    """The name for a code, or the text as the candidate wrote it when the country isn't known."""
    if not value:
        return ""
    names = COUNTRIES.get(value)
    if not names:
        return value
    return names[1] if locale.startswith("en") else names[0]
