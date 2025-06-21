class ChartsLocale:
    _en = {
        # Salaries chart
        "salaries_title": "Salary distribution",
        "salaries_xlabel": "Average brutto salary in €/Month",
        "salaries_ylabel": "Amount of jobs",
        "avg": "Average",
        "med": "Median",
        "q25": "25th percentile",
        "q75": "75th percentile",
        # Employment types
        "employment_types_title": "Distribution of employment types",
        "employment_types_ylabel": "Amount of jobs",
        "employment_types_xlabel": "Type of employment"
    }

    _de = {
        # Salaries chart
        "salaries_title": "Verteilung der Gehälter",
        "salaries_xlabel": "Durchschnittsgehalt brutto in €/Monat",
        "salaries_ylabel": "Anzahl der Stellenangebote",
        "avg": "Durchschnitt",
        "med": "Median",
        "q25": "25. Perzentil",
        "q75": "75. Perzentil",
        # Employment types
        "employment_types_title": "Verteilung der Beschäftigungsarten",
        "employment_types_ylabel": "Anzahl der Stellenangebote",
        "employment_types_xlabel": "Art der Beschäftigung"
    }

    locale = _en

    def __init__(self, locale="en"):
        self.set_locale(locale)

    def set_locale(self, locale):
        if locale in ["en", "de"]:
            locales = {"en": self._en, "de": self._de}
            self.locale = locales.get(locale)

    def get(self, code):
        return self.locale.get(code, code)