from synack.tree import *
from synack.tables import *

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
    day = date_group[0:2]
    hour = date_group[2:4]
    wind_indicator = date_group[4]

    wind_units = WIND_UNITS.get(wind_indicator)

    return DateLocation(
        day=day,
        hour=hour,
        wind_indicator=wind_indicator,
        wind_units=wind_units,
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
    cloud_cover_code = wind_group[0]
    wind_dir_code = wind_group[1:3]
    wind_speed_code = wind_group[3:5] if not extra_wind_group else extra_wind_group

    cloud_cover = CLOUD_COVER.get(cloud_cover_code)
    wind_direction = WindDirection(wind_dir_code)
    wind_speed = WindSpeed(wind_speed_code, wind_unit)

    return WindData(
        cloud_cover=cloud_cover,
        wind_direction=wind_direction,
        wind_speed=wind_speed,
        original=wind_group,
    )


def build_enumerated_group(group_type, data):
    if group_type in {"1", "2"}:  # Air temperature and dew point
        if not data.startswith("29"): # refer to the manual
            parsed = _parse_temperature(data)
        else:
            parsed = Humidity(data[2:])
        result = Metadata(
            parsed,
            name=ENUMERATED_GROUP[int(group_type) - 1],
        )
    elif group_type in {"3", "4"}:  # Station pressure and sea level pressure
        # NOTE Depending of the "regional agreement"
        # The fourth group could be either 4PPPP or 4a_3hhh
        # we assume 4PPPP here
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
        result = ErrorNode(
            name=f"enumerated_group_{group_type}", description=f"Invalid group type {group_type}"
        )
    return result


# ==================== CONVERSIONS ====================
def _parse_temperature(data, note=""):
    """Parse temperature data (1sTTT or 2sTTT format)"""
    sign_char = data[0]
    temp_value = data[1:4]

    if sign_char == "1":
        sign = -1
    else:
        sign = 1

    return TemperatureData(temp_value, sign_char, original=data, note=note)


def _parse_pressure(data):
    """Parse pressure data (PPPP format)"""
    return PressureData(data, original=data)


def _parse_pressure_tendency(data):
    """Parse pressure tendency (appp format)"""
    characteristic_code = data[0]
    characteristic = TENDENCY_MAP.get(characteristic_code)
    value = data[1:4]
    return PressureTendency(
        characteristic, characteristic_code, value, original=data
    )


def _parse_precipitation(data):
    """Parse precipitation data (RRRt format)"""
    amount_code = data[0:3]
    duration_code = data[3]
    duration = DURATION_MAP.get(duration_code)
    return PrecipitationData(amount_code, duration_code, duration, original=data)


def _parse_alternative_weather(data):
    """Parse alternative weather group (7wwW1W2)"""
    present_weather = data[0:2]
    past_weather_1 = data[2]
    past_weather_2 = data[3]

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
    low_clouds = data[0]  # N - low cloud amount
    cloud_types = data[1:4]  # CCC - cloud type codes

    low_cloud_type = cloud_types[0]
    mid_cloud_type = cloud_types[1]
    high_cloud_type = cloud_types[2]

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

def _parse_cloud_type(cloud_code, level):
    """Parse cloud type code"""
    description = CLOUD_TYPE_MAP.get(level, {}).get(cloud_code, "Unknown cloud type")

    return CloudType(cloud_code, description, level)


def _parse_observation_time(data):
    """Parse observation time group (9GGgg)"""
    hour = data[0:2]
    minute = data[2:4] if len(data) >= 4 else 0

    return ObservationTime(hour, minute, data)


# ==================== SECTION 3 BUILDER FUNCTIONS ====================


def build_section_3_group(group_type, data):
    """
    Build Section 3 groups (333xx groups) according to WMO standard
    """
    # no zero group
    # doesn't handle the mysterious 80000 group (and the extra groups that follow)
    if group_type in {"1", "2"}: # 1snTxTxTx 2snTnTnTn
        # recycled
        result = _parse_temperature(
            data,
            note="max" if group_type == "1" else "min"
        )
    elif group_type == "3":  # 3Ejjj (depends on the regional consensus)
        result = ErrorNode(
            name="section_3_group_3",
            description="The group 3Ejjj of section 3 is not implemented"
        )
    elif group_type == "4":  # 4E'sss - Snow depth
        result = _parse_snow_depth(data)
    elif group_type == "5":
        result = ErrorNode(
            name="section_3_group_5",
            description="The group 5jjjj jjjjj of section 3 is not implemented"
        )
    elif group_type == "6": # same as enumerated groups
        result = _parse_precipitation(data)
    elif group_type == "7":
        result = PrecipitationDaily(data, original=data)
    elif group_type == "8":  # 8NsChshs - Cloud layers
        result = _parse_cloud_layer(data)
    elif group_type == "9":  # 9SpSpspsp - Special phenomena
        result = _parse_special_phenomena(data)
    else:
        result = ErrorNode(
            name=f"section_3_group_{group_type}",
            description=f"Unsupported Section 3 group type: {group_type}",
        )
    return result


def _parse_snow_depth(data):
    """Parse snow depth group: 4E'sss"""
    ground_state_snow = data[0]  # E'
    snow_depth = data[1:4]  # sss

    return SnowDepthData(
        ground_state_snow,
        GROUND_STATE_SNOW.get(ground_state_snow),
        snow_depth,
        original=data
    )

def _parse_cloud_layer(data):
    """Parse cloud layer group: 8NsChshs"""
    cloud_amount = data[0]  # Ns
    cloud_type = data[1]  # C
    cloud_height_code = data[2:4]  # hshs

    return CloudLayerData(
        cloud_amount,
        CLOUD_COVER.get(cloud_amount),
        cloud_type,
        CLOUD_TYPES.get(cloud_type),
        cloud_height_code,
        original=data
    )


def _parse_special_phenomena(data):
    """Parse special phenomena group: 9SpSpspsp"""
    # TABLE 3778
    # 100 cases, each one with a different way of
    # interpreting s_p s_p based on S_p S_p
    return Metadata(
        {"special_phenomena": data, "original": data}, name="special_phenomena"
    )
