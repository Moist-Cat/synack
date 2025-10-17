from synack.tree import *
from synack.tables import (
    STATIONS,
    WIND_UNITS,
    CLOUD_COVER,
    PRESENT_WEATHER,
    PAST_WEATHER,
    CLOUD_TYPE_MAP,
    ENUMERATED_GROUP,
    TENDENCY_MAP,
    DURATION_MAP,
)

# ==================== AST BUILDER ====================
def build_station_info(message_type: str, station_group: str) -> Metadata:
    """Build metadata section of AST"""
    station_type = STATIONS.get(message_type)

    if len(station_group) == 5:
        block_number = station_group[0:2]
        station_number = station_group[2:5]
        station_id = f"{block_number}{station_number}"
    else:
        station_id = station_group
        block_number = station_number = "Unknown"

    return StationInfo(
        station_id=station_id,
        message_type=message_type,
        station_type=station_type,
        block_number=block_number,
        station_number=station_number,
        original_message_type=message_type,
        original_station_id=station_group,
    )


def build_date_location(date_group):
    errors = []
    if len(date_group) < 5:
        errors.append(f"Invalid date/time group: {date_group}")
        day = hour = 0
        wind_indicator = "/"
    else:
        day = date_group[0:2]
        hour = date_group[2:4]
        wind_indicator = date_group[4]

    wind_units = WIND_UNITS.get(wind_indicator)

    return DateLocation(
        day=day,
        hour=hour,
        wind_indicator=wind_indicator,
        wind_units=wind_units,
        errors=errors,
        original=date_group,
    )


def build_misc(misc_group: str):
    """Build wind visibility clouds section"""
    # Parse misc data
    precipitation_included = misc_group[0] in {"0", "1", "2"}
    is_staffed = misc_group[1] in {"1", "2", "3"}
    lowest_cloud = misc_group[2]
    visibility = misc_group[3:5]

    return MiscData(
        precipitation_included=precipitation_included,
        is_staffed=is_staffed,
        lowest_cloud=lowest_cloud,
        visibility=Visibility(visibility),
        original=misc_group,
    )


def build_wind(wind_group, extra_wind_group=None, wind_unit=None):
    # Parse wind data
    if len(wind_group) == 6:  # Ship format
        ship_id = wind_group[0:3]
        cloud_cover_code = wind_group[3]
        wind_dir_code = wind_group[4:6]
        wind_speed_code = extra_wind_group if extra_wind_group else ""
    else:  # Land format
        ship_id = None
        cloud_cover_code = wind_group[0]
        wind_dir_code = wind_group[1:3]
        wind_speed_code = wind_group[3:5] if not extra_wind_group else extra_wind_group

    cloud_cover = CLOUD_COVER.get(cloud_cover_code)
    wind_direction = WindDirection(wind_dir_code)
    wind_speed = WindSpeed(wind_speed_code, wind_unit)

    return WindData(
        ship_id=ship_id,
        cloud_cover=cloud_cover,
        wind_direction=wind_direction,
        wind_speed=wind_speed,
        original=wind_group,
    )


def build_enumerated_group(group_type, data):
    if group_type in {"1", "2"}:  # Air temperature and dew point
        result = Metadata(
            _parse_temperature(data),
            name=ENUMERATED_GROUP[int(group_type) - 1],
        )
    elif group_type in {"3", "4"}:  # Station pressure and sea level pressure
        result = PressureData(
            data, original=data, name=ENUMERATED_GROUP[int(group_type) - 1]
        )
    elif group_type == "5":  # Pressure tendency
        result = _parse_pressure_tendency(data)
    elif group_type == "6":  # Precipitation
        result = _parse_precipitation(data)
    elif group_type == "7":  # Present and past weather (alternative)
        result = _parse_alternative_weather(data)
    elif group_type == "8":  # Cloud information
        result = _parse_cloud_details(data)
    elif group_type == "9":  # Time of observation
        result = _parse_observation_time(data)
    else:
        group_type = "10"
        result = ErrorNode(
            name="enumerated_group", description=f"Invalid group type {group_type}"
        )
    return result


# ==================== CONVERSIONS ====================
def _parse_temperature(data):
    """Parse temperature data (1sTTT or 2sTTT format)"""
    if len(data) < 3 or data == "///":
        return TemperatureData(None, None, original=data)

    try:
        sign_char = data[0]
        temp_value = data[1:4]

        if sign_char == "1":
            sign = -1
        else:
            sign = 1

        return TemperatureData(temp_value, sign_char, original=data)
    except ValueError:
        return TemperatureData(None, None, original=data)


def _parse_pressure(data):
    """Parse pressure data (PPPP format)"""
    if data == "////" or not data:
        return PressureData(None, original=data)

    try:
        return PressureData(data, original=data)
    except ValueError:
        return PressureData(None, original=data)


def _parse_pressure_tendency(data):
    """Parse pressure tendency (appp format)"""
    if len(data) < 4 or data == "////":
        return PressureTendency(None, None, None, original=data)

    try:
        characteristic_code = data[0]
        characteristic = TENDENCY_MAP.get(characteristic_code)
        value = data[1:4]
        return PressureTendency(
            characteristic, characteristic_code, value, original=data
        )
    except ValueError:
        return PressureTendency(None, None, None, original=data)


def _parse_precipitation(data):
    """Parse precipitation data (RRRt format)"""
    if data == "////" or len(data) < 4:
        return PrecipitationData(None, None, None, original=data)
    try:
        amount_code = data[0:3]
        duration_code = data[3] if len(data) > 3 else "/"
        duration = DURATION_MAP.get(duration_code)
        return PrecipitationData(amount_code, duration_code, duration, original=data)
    except ValueError:
        return PrecipitationData(None, None, None, original=data)


def _parse_alternative_weather(data):
    """Parse alternative weather group (7wwW1W2)"""
    if len(data) < 4 or data == "////":
        return Metadata(name="weather group")

    present_weather = data[0:2]
    past_weather_1 = data[2]
    past_weather_2 = data[3] if len(data) > 3 else "/"

    present_weather_data = PRESENT_WEATHER.get(present_weather)
    past_weather_1_data = PAST_WEATHER.get(past_weather_1)
    past_weather_2_data = PAST_WEATHER.get(past_weather_2)

    return Metadata(
        WeatherCode(
            present_weather, present_weather_data, "present", name="present_weather"
        ),
        WeatherCode(past_weather_1, past_weather_1_data, "past", name="past_weather_1"),
        WeatherCode(past_weather_2, past_weather_2_data, "past", name="past_weather_2"),
        name="weather_group",
    )


def _parse_cloud_details(data):
    """Parse cloud information (8NCCC format)"""
    if data == "////" or len(data) < 4:
        return Metadata(name="cloud_information")

    try:
        low_clouds = data[0]  # N - low cloud amount
        cloud_types = data[1:4]  # CCC - cloud type codes

        low_cloud_type = cloud_types[0] if len(cloud_types) > 0 else "/"
        mid_cloud_type = cloud_types[1] if len(cloud_types) > 1 else "/"
        high_cloud_type = cloud_types[2] if len(cloud_types) > 2 else "/"

        return Metadata(
            Metadata(
                {"amount": CLOUD_COVER.get(low_clouds)},
                _parse_cloud_type(low_cloud_type, "low"),
                name="low_clouds",
            ),
            Metadata(_parse_cloud_type(mid_cloud_type, "mid"), name="mid_clouds"),
            Metadata(_parse_cloud_type(high_cloud_type, "high"), name="high_clouds"),
            name="cloud_information",
        )
    except ValueError:
        return Metadata(name="cloud_information")


def _parse_cloud_type(cloud_code, level):
    """Parse cloud type code"""
    if cloud_code == "/" or not cloud_code:
        return CloudType(cloud_code, "Not reported", level)

    description = CLOUD_TYPE_MAP.get(level, {}).get(cloud_code, "Unknown cloud type")

    return CloudType(cloud_code, description, level)


def _parse_observation_time(data):
    """Parse observation time group (9GGgg)"""
    if data == "////" or not data:
        return ObservationTime(None, None, data)
    try:
        hour = data[0:2]
        minute = data[2:4] if len(data) >= 4 else 0

        return ObservationTime(hour, minute, data)
    except ValueError:
        return ObservationTime(None, None, data)
