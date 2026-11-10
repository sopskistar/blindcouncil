"""Product presets are practical durations; short seconds remain an explicit test option."""
DEFAULT = 86400
MAXIMUM = 604800
PRESETS = {"15m": 900, "1h": 3600, "24h": DEFAULT, "3d": 259200, "7d": MAXIMUM}


def product_duration(value="24h"):
    if not isinstance(value, str) or value not in PRESETS:
        raise ValueError("Choose 15m, 1h, 24h, 3d or 7d; the default is 24h")
    return PRESETS[value]
