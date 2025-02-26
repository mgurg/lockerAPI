from enum import Enum


class ContactType(Enum):
    PHONE = "phone"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    VIBER = "viber"
    FACEBOOK = "facebook"


class GameDifficulty(Enum):
    INTRO = "intro"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class FearLevel(Enum):
    NONE = "none"  # No fear elements
    SPOOKY = "spooky"  # Mildly eerie, family-friendly
    TENSE = "tense"  # Suspenseful, but no major scares
    SCARY = "scary"  # Intense atmosphere, jump scares possible
    TERRIFYING = "terrifying"  # Extreme horror, psychological or physical fear elements


class SupportedLanguage(Enum):
    PL = "pl"
    EN = "en"
    DE = "de"
