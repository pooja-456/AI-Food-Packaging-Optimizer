"""
Controlled vocabularies and standard nomenclatures for food packaging science.

These vocabularies provide standardized identifiers for food properties,
commodity categories, processing states, product forms, maturity stages,
material categories, and packaging properties without enforcing arbitrary
numerical constraints or universal rankings.
"""

from enum import Enum


class FoodProperty(str, Enum):
    """Standard food properties relevant to shelf life and packaging requirements."""
    MOISTURE_CONTENT = "moisture_content"
    FAT_CONTENT = "fat_content"
    PH = "ph"
    WATER_ACTIVITY = "water_activity"
    RESPIRATION_RATE = "respiration_rate"
    ETHYLENE_PRODUCTION = "ethylene_production"
    ETHYLENE_SENSITIVITY = "ethylene_sensitivity"
    OXYGEN_SENSITIVITY = "oxygen_sensitivity"
    MOISTURE_SENSITIVITY = "moisture_sensitivity"
    OXIDATION_SENSITIVITY = "oxidation_sensitivity"
    AROMA_VOLATILITY = "aroma_volatility"
    MICROBIAL_RISK = "microbial_risk"
    TEMPERATURE_SENSITIVITY = "temperature_sensitivity"
    SHELF_LIFE = "shelf_life"
    MECHANICAL_SENSITIVITY = "mechanical_sensitivity"
    CHILLING_INJURY_THRESHOLD = "chilling_injury_threshold"
    FREEZING_POINT = "freezing_point"
    CO2_SENSITIVITY = "co2_sensitivity"
    TRANSPIRATION_COEFFICIENT = "transpiration_coefficient"


class CommodityCategory(str, Enum):
    """Broad food commodity classifications."""
    FRUIT = "fruit"
    VEGETABLE = "vegetable"
    MEAT_POULTRY = "meat_poultry"
    SEAFOOD = "seafood"
    DAIRY = "dairy"
    BAKERY_CEREAL = "bakery_cereal"
    CONFECTIONERY = "confectionery"
    BEVERAGE = "beverage"
    PROCESSED_FOOD = "processed_food"
    NUTS_SEEDS = "nuts_seeds"
    OTHER = "other"


class ProcessingState(str, Enum):
    """Processing and preservation state of the commodity."""
    RAW = "raw"
    FRESH_CUT = "fresh_cut"
    MINIMALLY_PROCESSED = "minimally_processed"
    PASTEURIZED = "pasteurized"
    STERILIZED = "sterilized"
    FROZEN = "frozen"
    DRIED = "dried"
    FERMENTED = "fermented"
    CURED = "cured"
    COOKED = "cooked"
    BLANCHED = "blanched"


class ProductForm(str, Enum):
    """Physical state / geometry of the food product."""
    WHOLE = "whole"
    SLICED = "sliced"
    DICED = "diced"
    SHREDDED = "shredded"
    PUREE = "puree"
    JUICE = "juice"
    FILLET = "fillet"
    PORTIONED = "portioned"
    GROUND = "ground"
    POWDER = "powder"
    LIQUID = "liquid"
    PASTE = "paste"


class MaturityStage(str, Enum):
    """Physiological maturity or ripeness stage."""
    IMMATURE = "immature"
    MATURE_GREEN = "mature_green"
    BREAKER = "breaker"
    TURNING = "turning"
    RIPE = "ripe"
    FULLY_RIPE = "fully_ripe"
    OVERRIPE = "overripe"


class ValueType(str, Enum):
    """Statistical or measurement nature of an observation value."""
    MEAN = "mean"
    MEDIAN = "median"
    POINT_ESTIMATE = "point_estimate"
    RANGE = "range"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    NOMINAL = "nominal"
    QUALITATIVE = "qualitative"


class SourceType(str, Enum):
    """Scientific / technical publication or origin of evidence."""
    JOURNAL_ARTICLE = "journal_article"
    HANDBOOK = "handbook"
    GOVERNMENT_DATABASE = "government_database"
    LABORATORY_MEASUREMENT = "laboratory_measurement"
    TECHNICAL_DATASHEET = "technical_datasheet"
    CONFERENCE_PROCEEDING = "conference_proceeding"
    BOOK_CHAPTER = "book_chapter"
    PATENT = "patent"


class EvidenceStrength(str, Enum):
    """Qualitative assessment of evidence reliability and peer-review rigor."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


class MaterialCategory(str, Enum):
    """Broad packaging material structural classification."""
    MONO_POLYMER = "mono_polymer"
    COEXTRUDED_MULTILAYER = "coextruded_multilayer"
    LAMINATED_MULTILAYER = "laminated_multilayer"
    METALLIZED_FILM = "metallized_film"
    FOIL_LAMINATE = "foil_laminate"
    BIO_BASED_POLYMER = "bio_based_polymer"
    BIODEGRADABLE_POLYMER = "biodegradable_polymer"
    PAPER_FIBER_BASED = "paper_fiber_based"
    ACTIVE_FUNCTIONAL = "active_functional"
    COATED_FILM = "coated_film"


class PackagingProperty(str, Enum):
    """Key packaging performance and barrier metrics."""
    OTR = "oxygen_transmission_rate"
    WVTR = "water_vapor_transmission_rate"
    CO2TR = "carbon_dioxide_transmission_rate"
    AROMA_BARRIER = "aroma_barrier"
    TENSILE_STRENGTH = "tensile_strength"
    ELONGATION_AT_BREAK = "elongation_at_break"
    PUNCTURE_RESISTANCE = "puncture_resistance"
    TEAR_RESISTANCE = "tear_resistance"
    SEAL_STRENGTH = "seal_strength"
    SEAL_INITIATION_TEMPERATURE = "seal_initiation_temperature"
    TRANSPARENCY = "transparency"
    HAZE = "haze"
    MAX_SERVICE_TEMPERATURE = "max_service_temperature"
    MIN_SERVICE_TEMPERATURE = "min_service_temperature"
    BIOBASED_CONTENT = "biobased_content"
    RECYCLABILITY = "recyclability"
    COMPOSTABILITY = "compostability"
