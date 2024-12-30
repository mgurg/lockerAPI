class PolishCityInflector:
    def __init__(self):
        # Common endings and their inflections
        # Format: {ending: [genitive, dative, accusative, instrumental, locative, vocative]}
        self.patterns = {
    # Most common city endings
    "ów": ["owa", "owowi", "ów", "owem", "owie", "owie"],  # Chorzów, Zambrów, etc.
    "in": ["ina", "inowi", "in", "inem", "inie", "inie"],  # Wolin, Lublin, etc.
    "sk": ["ska", "skowi", "sk", "skiem", "sku", "sku"],  # Słupsk, Gdańsk, etc.
    "ice": ["ic", "icom", "ice", "icami", "icach", "ice"],  # Gliwice, Chojnice, etc.
    "no": ["na", "nu", "no", "nem", "nie", "no"],  # Mielno, Olecko, etc.
    "yn": ["yna", "ynowi", "yn", "ynem", "ynie", "ynie"],  # Kętrzyn, etc.
    "ek": ["ka", "kowi", "ek", "kiem", "ku", "ku"],  # Pasłęk, Okonek, etc.
    "wo": ["wa", "wu", "wo", "wem", "wie", "wo"],  # Władysławowo, Darłowo, etc.
    "ca": ["cy", "cy", "cę", "cą", "cy", "co"],  # Łobżenica, etc.
    "nia": ["ni", "ni", "nię", "nią", "ni", "nio"],  # Jastarnia, Gdynia, etc.
    "zna": ["zny", "znie", "znę", "zną", "znie", "zno"],  # Kościerzyna, etc.
    "ane": ["anego", "anemu", "ane", "anym", "anym", "ane"],  # Zakopane
    "uń": ["unia", "uniowi", "uń", "uniem", "uniu", "uniu"],  # Toruń
    "awa": ["awy", "awie", "awę", "awą", "awie", "awo"],  # Warszawa
    "ław": ["ławia", "ławiowi", "ław", "ławiem", "ławiu", "ławiu"],  # Wrocław

    # Special cases for major cities
    "ódź": ["odzi", "odzi", "ódź", "odzią", "odzi", "odzi"],  # Łódź
    "znań": ["znania", "znaniowi", "znań", "znaniem", "znaniu", "znaniu"],  # Poznań
    "góra": ["góry", "górze", "górę", "górą", "górze", "góro"],  # Zielona Góra
    "góry": ["gór", "górom", "góry", "górami", "górach", "góry"],  # Tarnowskie Góry
    " bór": ["ego boru", "emu borowi", " bór", "ym borem", "ym borze", " borze"],  # Biały Bór
    "zdrój": ["zdroju", "zdrojowi", "zdrój", "zdrojem", "zdroju", "zdroju"],  # Szczawno-Zdrój
    "ski": ["skiego", "skiemu", "ski", "skim", "skim", "ski"],  # Gorzów Śląski
}

    def get_ending(self, city):
        """Determine the ending pattern of a city name."""
        city = city.lower()
        for ending in self.patterns.keys():
            if city.endswith(ending):
                return ending
        return None

    def inflect(self, city, case):
        """
        Inflect a Polish city name.

        Args:
            city (str): The city name in nominative case
            case (str): One of: 'genitive', 'dative', 'accusative',
                       'instrumental', 'locative', 'vocative'

        Returns:
            str: The inflected city name
        """
        cases = ["genitive", "dative", "accusative", "instrumental", "locative", "vocative"]
        if case not in cases:
            print(f"Error: Invalid case. Use one of: {', '.join(cases)}")
            return city

        ending = self.get_ending(city)
        if not ending:
            print(f"Cannot inflect '{city}' - unknown ending pattern")
            return city

        case_index = cases.index(case)
        new_ending = self.patterns[ending][case_index]

        return city[: -len(ending)] + new_ending
