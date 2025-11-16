STATIONS = {
    "AAXX": "land_station",
    "BBXX": "ship_station",
    "OOXX": "mobile_land_station",
}

# Wind units
WIND_UNITS = {
    "0": "m/s (estimated)",
    "1": "m/s",
    "3": "knots (estimated)",
    "4": "knots",
    # yes, it's correct
    # CODE 1855
    "2": "not measured",
}

# Cloud cover
CLOUD_COVER = {
    "0": "Clear",
    "1": "1/8 or less",
    "2": "2/8",
    "3": "3/8",
    "4": "4/8",
    "5": "5/8",
    "6": "6/8",
    "7": "7/8 or more, not overcast",
    "8": "Overcast",
    "9": "Sky obscured",
}


class PresentWeatherCategory:
    """WMO Code Table 4677 - Present Weather"""

    # Precipitation
    PRECIPITATION = "precipitation"
    NO_PRECIPITATION = "no_precipitation"
    FOG = "fog"
    THUNDERSTORM = "thunderstorm"
    STORM = "storm"
    DUSTSTORM = "duststorm"
    SQUALL = "squall"
    TORNADO = "tornado"
    FUNNEL_CLOUD = "funnel_cloud"
    DUST_WHIRLS = "dust_whirls"
    DRIFTING_SNOW = "drifting_snow"
    BLOWING_SNOW = "blowing_snow"
    DRIFTING_DUST = "drifting_dust"
    BLOWING_DUST = "blowing_dust"
    SANSTORM = "sandstorm"
    HAIL = "hail"
    FREEZING_PRECIPITATION = "freezing_precipitation"
    SHOWERS = "showers"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    SNOW = "snow"
    SLEET = "sleet"


# ...!
"""WMO Code Table 4677 - Present Weather with detailed descriptions"""
# ww = 00-19: No precipitation at the station at the time of observation
# ww = 10-19: No precipitation, fog, ice fog or thunderstorm at the station at the time of observation
# ww = 20-29: Precipitation, fog, ice fog or thunderstorm at the station during the preceding hour but not at the time of observation
# ww = 30-39: Duststorm, sandstorm, drifting or blowing snow
# ww = 40-49: Fog or ice fog at the time of observation
# ww = 50-59: Drizzle
# ww = 60-69: Rain
# ww = 70-79: Solid precipitation not in showers
# ww = 80-99: Showery precipitation, or precipitation with current or recent thunderstorm
# ww = 90-99: Precipitation with thunderstorm
PRESENT_WEATHER = {
    "00": (
        "Phenomena not observed",
        PresentWeatherCategory.NO_PRECIPITATION,
    ),
    "01": (
        "Clouds generally dissolving or becoming less developed",
        PresentWeatherCategory.NO_PRECIPITATION,
    ),
    "02": (
        "State of sky on the whole unchanged",
        PresentWeatherCategory.NO_PRECIPITATION,
    ),
    "03": (
        "Clouds generally forming or developing",
        PresentWeatherCategory.NO_PRECIPITATION,
    ),
    "04": (
        "Visibility reduced by smoke",
        PresentWeatherCategory.NO_PRECIPITATION,
    ),
    "05": (
        "Haze",
        PresentWeatherCategory.NO_PRECIPITATION,
    ),
    "06": (
        "Widespread dust in suspension in the air, not raised by wind",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "07": (
        "Dust or sand raised by wind",
        PresentWeatherCategory.DUST_WHIRLS,
    ),
    "08": (
        "Well developed dust whirl(s) or sand whirl(s)",
        PresentWeatherCategory.DUST_WHIRLS,
    ),
    "09": (
        "Duststorm or sandstorm within sight but not at station",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "10": (
        "Mist",
        PresentWeatherCategory.FOG,
    ),
    "11": (
        "Patches of shallow fog or ice fog",
        PresentWeatherCategory.FOG,
    ),
    "12": (
        "More or less continuous shallow fog or ice fog",
        PresentWeatherCategory.FOG,
    ),
    "13": (
        "Lightning visible, no thunder heard",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "14": (
        "Precipitation within sight, not reaching ground",
        PresentWeatherCategory.PRECIPITATION,
    ),
    "15": (
        "Precipitation within sight, reaching ground, distant",
        PresentWeatherCategory.PRECIPITATION,
    ),
    "16": (
        "Precipitation within sight, reaching ground, near",
        PresentWeatherCategory.PRECIPITATION,
    ),
    "17": (
        "Thunderstorm, but no precipitation at station",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "18": (
        "Squalls within sight",
        PresentWeatherCategory.SQUALL,
    ),
    "19": (
        "Funnel cloud(s) within sight",
        PresentWeatherCategory.FUNNEL_CLOUD,
    ),
    "20": (
        "Drizzle (not freezing) or snow grains",
        PresentWeatherCategory.DRIZZLE,
    ),
    "21": (
        "Rain (not freezing)",
        PresentWeatherCategory.RAIN,
    ),
    "22": (
        "Snow",
        PresentWeatherCategory.SNOW,
    ),
    "23": (
        "Rain and snow or ice pellets",
        PresentWeatherCategory.SLEET,
    ),
    "24": (
        "Freezing drizzle or freezing rain",
        PresentWeatherCategory.FREEZING_PRECIPITATION,
    ),
    "25": (
        "Shower(s) of rain",
        PresentWeatherCategory.SHOWERS,
    ),
    "26": (
        "Shower(s) of snow, or of rain and snow",
        PresentWeatherCategory.SHOWERS,
    ),
    "27": (
        "Shower(s) of hail, or of rain and hail",
        PresentWeatherCategory.HAIL,
    ),
    "28": (
        "Fog or ice fog",
        PresentWeatherCategory.FOG,
    ),
    "29": (
        "Thunderstorm (with or without precipitation)",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "30": (
        "Slight or moderate duststorm or sandstorm",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "31": (
        "Slight or moderate duststorm or sandstorm, no change",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "32": (
        "Slight or moderate duststorm or sandstorm, increasing",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "33": (
        "Severe duststorm or sandstorm",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "34": (
        "Severe duststorm or sandstorm, no change",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "35": (
        "Severe duststorm or sandstorm, increasing",
        PresentWeatherCategory.DUSTSTORM,
    ),
    "36": (
        "Slight or moderate blowing snow",
        PresentWeatherCategory.BLOWING_SNOW,
    ),
    "37": (
        "Heavy blowing snow",
        PresentWeatherCategory.BLOWING_SNOW,
    ),
    "38": (
        "Slight or moderate drifting snow",
        PresentWeatherCategory.DRIFTING_SNOW,
    ),
    "39": (
        "Heavy drifting snow",
        PresentWeatherCategory.DRIFTING_SNOW,
    ),
    "40": (
        "Fog or ice fog at a distance",
        PresentWeatherCategory.FOG,
    ),
    "41": (
        "Patches of fog or ice fog",
        PresentWeatherCategory.FOG,
    ),
    "42": (
        "Fog or ice fog, sky discernible, thinning",
        PresentWeatherCategory.FOG,
    ),
    "43": (
        "Fog or ice fog, sky not discernible, thinning",
        PresentWeatherCategory.FOG,
    ),
    "44": (
        "Fog or ice fog, sky discernible, no change",
        PresentWeatherCategory.FOG,
    ),
    "45": (
        "Fog or ice fog, sky not discernible, no change",
        PresentWeatherCategory.FOG,
    ),
    "46": (
        "Fog or ice fog, sky discernible, thickening",
        PresentWeatherCategory.FOG,
    ),
    "47": (
        "Fog or ice fog, sky not discernible, thickening",
        PresentWeatherCategory.FOG,
    ),
    "48": (
        "Fog, depositing rime, sky discernible",
        PresentWeatherCategory.FOG,
    ),
    "49": (
        "Fog, depositing rime, sky not discernible",
        PresentWeatherCategory.FOG,
    ),
    "50": (
        "Drizzle, not freezing, intermittent slight",
        PresentWeatherCategory.DRIZZLE,
    ),
    "51": (
        "Drizzle, not freezing, continuous slight",
        PresentWeatherCategory.DRIZZLE,
    ),
    "52": (
        "Drizzle, not freezing, intermittent moderate",
        PresentWeatherCategory.DRIZZLE,
    ),
    "53": (
        "Drizzle, not freezing, continuous moderate",
        PresentWeatherCategory.DRIZZLE,
    ),
    "54": (
        "Drizzle, not freezing, intermittent heavy",
        PresentWeatherCategory.DRIZZLE,
    ),
    "55": (
        "Drizzle, not freezing, continuous heavy",
        PresentWeatherCategory.DRIZZLE,
    ),
    "56": (
        "Drizzle, freezing, slight",
        PresentWeatherCategory.FREEZING_PRECIPITATION,
    ),
    "57": (
        "Drizzle, freezing, moderate or heavy",
        PresentWeatherCategory.FREEZING_PRECIPITATION,
    ),
    "58": (
        "Drizzle and rain, slight",
        PresentWeatherCategory.DRIZZLE,
    ),
    "59": (
        "Drizzle and rain, moderate or heavy",
        PresentWeatherCategory.DRIZZLE,
    ),
    "60": (
        "Rain, not freezing, intermittent slight",
        PresentWeatherCategory.RAIN,
    ),
    "61": (
        "Rain, not freezing, continuous slight",
        PresentWeatherCategory.RAIN,
    ),
    "62": (
        "Rain, not freezing, intermittent moderate",
        PresentWeatherCategory.RAIN,
    ),
    "63": (
        "Rain, not freezing, continuous moderate",
        PresentWeatherCategory.RAIN,
    ),
    "64": (
        "Rain, not freezing, intermittent heavy",
        PresentWeatherCategory.RAIN,
    ),
    "65": (
        "Rain, not freezing, continuous heavy",
        PresentWeatherCategory.RAIN,
    ),
    "66": (
        "Rain, freezing, slight",
        PresentWeatherCategory.FREEZING_PRECIPITATION,
    ),
    "67": (
        "Rain, freezing, moderate or heavy",
        PresentWeatherCategory.FREEZING_PRECIPITATION,
    ),
    "68": (
        "Rain or drizzle and snow, slight",
        PresentWeatherCategory.SLEET,
    ),
    "69": (
        "Rain or drizzle and snow, moderate or heavy",
        PresentWeatherCategory.SLEET,
    ),
    "70": (
        "Intermittent fall of snowflakes, slight",
        PresentWeatherCategory.SNOW,
    ),
    "71": (
        "Continuous fall of snowflakes, slight",
        PresentWeatherCategory.SNOW,
    ),
    "72": (
        "Intermittent fall of snowflakes, moderate",
        PresentWeatherCategory.SNOW,
    ),
    "73": (
        "Continuous fall of snowflakes, moderate",
        PresentWeatherCategory.SNOW,
    ),
    "74": (
        "Intermittent fall of snowflakes, heavy",
        PresentWeatherCategory.SNOW,
    ),
    "75": (
        "Continuous fall of snowflakes, heavy",
        PresentWeatherCategory.SNOW,
    ),
    "76": (
        "Diamond dust (with or without fog)",
        PresentWeatherCategory.SNOW,
    ),
    "77": (
        "Snow grains (with or without fog)",
        PresentWeatherCategory.SNOW,
    ),
    "78": (
        "Isolated starlike snow crystals (with or without fog)",
        PresentWeatherCategory.SNOW,
    ),
    "79": (
        "Ice pellets",
        PresentWeatherCategory.FREEZING_PRECIPITATION,
    ),
    "80": (
        "Rain shower(s), slight",
        PresentWeatherCategory.SHOWERS,
    ),
    "81": (
        "Rain shower(s), moderate or heavy",
        PresentWeatherCategory.SHOWERS,
    ),
    "82": (
        "Rain shower(s), violent",
        PresentWeatherCategory.SHOWERS,
    ),
    "83": (
        "Shower(s) of rain and snow mixed, slight",
        PresentWeatherCategory.SHOWERS,
    ),
    "84": (
        "Shower(s) of rain and snow mixed, moderate or heavy",
        PresentWeatherCategory.SHOWERS,
    ),
    "85": (
        "Snow shower(s), slight",
        PresentWeatherCategory.SHOWERS,
    ),
    "86": (
        "Snow shower(s), moderate or heavy",
        PresentWeatherCategory.SHOWERS,
    ),
    "87": (
        "Shower(s) of snow grains or ice pellets, slight",
        PresentWeatherCategory.SHOWERS,
    ),
    "88": (
        "Shower(s) of snow grains or ice pellets, moderate or heavy",
        PresentWeatherCategory.SHOWERS,
    ),
    "89": (
        "Shower(s) of hail, with or without rain or rain and snow, slight",
        PresentWeatherCategory.HAIL,
    ),
    "90": (
        "Shower(s) of hail, with or without rain or rain and snow, moderate or heavy",
        PresentWeatherCategory.HAIL,
    ),
    "91": (
        "Thunderstorm during past hour, slight with precipitation",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "92": (
        "Thunderstorm during past hour, moderate or heavy with precipitation",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "93": (
        "Thunderstorm during past hour, slight with hail",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "94": (
        "Thunderstorm during past hour, moderate or heavy with hail",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "95": (
        "Thunderstorm, slight or moderate with duststorm or sandstorm",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "96": (
        "Thunderstorm, heavy with duststorm or sandstorm",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "97": (
        "Thunderstorm, slight or moderate with squall(s)",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "98": (
        "Thunderstorm, heavy with squall(s)",
        PresentWeatherCategory.THUNDERSTORM,
    ),
    "99": (
        "Thunderstorm with tornado or waterspout",
        PresentWeatherCategory.TORNADO,
    ),
}

# 4561
PAST_WEATHER = {
    "0": ("Cloud cover 1/2 or less", "No significant weather"),
    "1": ("Cloud cover more than 1/2", "No significant weather"),
    "2": ("Rain", "Liquid precipitation"),
    "3": ("Snow", "Solid precipitation"),
    "4": ("Drizzle", "Liquid precipitation"),
    "5": ("Shower(s)", "Liquid precipitation"),
    "6": ("Thunderstorm", "Thunderstorm"),
    "7": ("Fog", "No precipitation"),
    "8": ("Precipitation in sight", "Precipitation"),
    "9": ("Storm", "Storm"),
}

# https://cloudatlas.wmo.int/es/coding-instructions-cl.html
CLOUD_TYPE_MAP = {
    "low": {
        "0": "No low clouds",
        "1": "Cumulus humilis",
        "2": "Cumulus mediocris",
        "3": "Cumulonimbus calvus",
        "4": "Stratocumulus cumulogenitus",
        "5": "Stratocumulus",
        "6": "Stratus, Fractostratus, Fractocumulus",
        "7": "Fractostratus, Fractocumulus of bad weather",
        "8": "Cumulus, Stratocumulus",
        "9": "Cumulonimbus capillatus",
    },
    "mid": {
        "0": "No mid clouds",
        "1": "Altostratus translucidus",
        "2": "Altostratus opacus",
        "3": "Altocumulus translucidus",
        "4": "Altocumulus lenticularis",
        "5": "Altocumulus translucidus at different levels",
        "6": "Altocumulus cumulogenitus",
        "7": "Altocumulus opacus",
        "8": "Altocumulus castellanus",
        "9": "Altocumulus of chaotic sky",
    },
    "high": {
        "0": "No high clouds",
        "1": "Cirrus fibratus",
        "2": "Cirrus spissatus",
        "3": "Cirrus uncinus",
        "4": "Cirrus, Cirrostratus",
        "5": "Cirrostratus covering whole sky",
        "6": "Cirrostratus not covering whole sky",
        "7": "Cirrostratus covering whole sky",
        "8": "Cirrocumulus",
        "9": "Cirrocumulus and Cirrostratus",
    },
}

ENUMERATED_GROUP = [
    "air_temperature",
    "dew_point_temperature",
    "station_pressure",
    "sea_level_pressure",
    "pressure_tendency",
    "precipitation",
    "present_and_past_wheater",
    "cloud_information",
    "time_of_observation",
    "unknown_group",
]

TENDENCY_MAP = {
    "0": "Increasing, then decreasing",
    "1": "Increasing, then steady",
    "2": "Increasing steadily",
    "3": "Decreasing or steady, then increasing",
    "4": "Steady",
    "5": "Decreasing, then increasing",
    "6": "Decreasing, then steady",
    "7": "Decreasing steadily",
    "8": "Steady or increasing, then decreasing",
}

DURATION_MAP = {
    "1": "6 hours",
    "2": "12 hours",
    "3": "18 hours",
    "4": "24 hours",
    "5": "0 hours",
    "6": "2 hours",
    "7": "3 hours",
    "8": "9 hours",
    "9": "15 hours",
    "/": "Not specified",
}

GROUND_STATE_SNOW = {
    "0": "Surface predominantly ice covered",
    "1": "Compact or wet snow (with or without ice) covering less than one-half",
    "2": "Compact or wet snow (with or without ice) covering at least one-half",
    "3": "Even layer of compact or wet snow covering ground completely",
    "4": "Uneven layer of compact or wet snow covering ground completely",
    "5": "Loose dry snow covering less than one-half",
    "6": "Loose dry snow covering at least one-half",
    "7": "Even layer of loose dry snow covering ground completely",
    "8": "Uneven layer of loose dry snow covering ground completely",
    "9": "Snow covering ground completely, deep drifts",
}

CLOUD_TYPES = {
    "0": "Cirrus Ci",
    "1": "Cirrocumulus Cc",
    "2": "Cirrostratus Cs",
    "3": "Altocumulus Ac",
    "4": "Altostratus As",
    "5": "Nimbostratus Ns",
    "6": "Stratocumulus Sc",
    "7": "Stratus St",
    "8": "Cumulus Cu",
    "9": "Cumulonimbus Cb",
}

SPECIAL_VISIBILITY = {
    90: 0.00,
    91: 0.05,
    92: 0.2,
    93: 0.5,
    94: 1,
    95: 2,
    96: 4,
    97: 10,
    98: 20,
    99: 50,
}

SPECIAL_CLOUD_HEIGHT = {
    90: 50,
    91: 100,
    92: 200,
    93: 300,
    94: 600,
    95: 1000,
    96: 1500,
    97: 2000,
    98: 2500,
    99: 0,
}

COMPASS = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]

# 1806
EVAPORATION_CODES = {
    "0": ("US open pan evaporimeter (without lid)", "Evaporation"),
    "1": ("US open pan evaporimeter (with screen)", "Evaporation"),
    "2": ("GGI-3000 evaporimeter (sunken)", "Evaporation"),
    "3": ("20 m² tank", "Evaporation"),
    "4": ("Other", "Evaporation"),
    "5": ("Rice", "Evapotranspiration"),
    "6": ("Wheat", "Evapotranspiration"),
    "7": ("Corn", "Evapotranspiration"),
    "8": ("Sorghum", "Evapotranspiration"),
    "9": ("Other crops", "Evapotranspiration"),
}

# rad
RADIATION_TYPES_HOURLY = {
    "0": ("net_positive", "Net positive radiation during preceding hour", "kJ/m2"),
    "1": ("net_negative", "Net negative radiation during preceding hour", "kJ/m2"),
    "2": ("solar_global", "Global solar radiation during preceding hour", "kJ/m2"),
    "3": ("solar_diffuse", "Diffuse solar radiation during preceding hour", "kJ/m2"),
    "4": (
        "longwave_down",
        "Downward longwave radiation during preceding hour",
        "kJ/m2",
    ),
    "5": ("longwave_up", "Upward longwave radiation during preceding hour", "kJ/m2"),
    "6": ("shortwave", "Shortwave radiation during preceding hour", "kJ/m2"),
}

RADIATION_TYPES_DAILY = {
    "0": ("net_positive", "Net positive radiation during preceding 24 hours", "J/cm2"),
    "1": ("net_negative", "Net negative radiation during preceding 24 hours", "J/cm2"),
    "2": ("solar_global", "Global solar radiation during preceding 24 hours", "J/cm2"),
    "3": (
        "solar_diffuse",
        "Diffuse solar radiation during preceding 24 hours",
        "J/cm2",
    ),
    "4": (
        "longwave_down",
        "Downward longwave radiation during preceding 24 hours",
        "J/cm2",
    ),
    "5": (
        "longwave_up",
        "Upward longwave radiation during preceding 24 hours",
        "J/cm2",
    ),
    "6": ("shortwave", "Shortwave radiation during preceding 24 hours", "J/cm2"),
}

# Special radiation types from 12.4.7.1.2
SPECIAL_RADIATION_TYPES = {
    "5407": (
        "net_shortwave_hourly",
        "Net shortwave radiation during preceding hour",
        "kJ m⁻²",
    ),
    "5408": (
        "solar_direct_hourly",
        "Direct solar radiation during preceding hour",
        "kJ m⁻²",
    ),
    "5507": (
        "net_shortwave_daily",
        "Net shortwave radiation during preceding 24 hours",
        "J cm⁻²",
    ),
    "5508": (
        "solar_direct_daily",
        "Direct solar radiation during preceding 24 hours",
        "J cm⁻²",
    ),
}

# 0700
DIRECTION = {
    "1": "NE",
    "2": "E",
    "3": "SE",
    "4": "S",
    "5": "SW",
    "6": "W",
    "7": "NW",
    "8": "N",
}

SPECIAL_DIRECTION = {
    "clouds": {
        "9": "Unknown or invisible",
        "0": "Stationary or cloudless",
    },  # D_L D_M D_H
    "phenomena": {"9": "All directions", "0": "In the station"},  # D_a
}

# 1004
CLOUD_ANGLE = {
    "0": 90,
    "1": 45,
    "2": 30,
    "3": 20,
    "4": 15,
    "5": 12,
    "6": 9,
    "7": 7,
    "8": 6,
    "9": 5,
}

TEMPERATURE_CHANGE = {
    "0": 10,
    "1": 11,
    "2": 12,
    "3": 13,
    "4": 14,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}

# 0901
SOIL_STATE = {
    "0": "Ground surface dry (no cracks and no appreciable amount of dust or loose sand)",
    "1": "Ground surface moist",
    "2": "Ground surface wet (water standing in puddles large or small on the surface)",
    "3": "Ground flooded",
    "4": "Ground surface frozen",
    "5": "Glaze (smooth ice) on ground",
    "6": "Loose dry dust or sand not completely covering the ground",
    "7": "Thin layer of loose dry dust or sand completely covering the ground",
    "8": "Moderate or thick layer of loose dry dust or sand completely covering the ground",
    "9": "Ground extremely dry and cracked",
}

# 1600
LOWEST_CLOUD_HEIGHT = {
    "0": (0, 50),
    "1": (50, 100),
    "2": (100, 200),
    "3": (200, 300),
    "4": (300, 600),
    "5": (600, 100),
    "6": (1000, 1500),
    "7": (1500, 2000),
    "8": (2000, 2500),
    "9": (2500, 9999),
}
