_en = {
    "salaries_title": "Salary distribution",
    "salaries_xlabel": "Average brutto salary in €/Month",
    "salaries_ylabel": "Amount of jobs",
    "avg": "Average",
    "med": "Median",
    "q25": "25th percentile",
    "q75": "75th percentile"
}

_de = {
    "salaries_title": "Verteilung der Gehälter",
    "salaries_xlabel": "Durchschnittsgehalt brutto in €/Monat",
    "salaries_ylabel": "Anzahl der Stellenangebote",
    "avg": "Durchschnitt",
    "med": "Median",
    "q25": "25. Perzentil",
    "q75": "75. Perzentil"
}


def get_locale(locale):
    locales = {"en": _en, "de": _de}
    return locales.get(locale)
