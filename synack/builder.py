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
    lowest_cloud_height = LOWEST_CLOUD_HEIGHT.get(lowest_cloud)
    visibility = misc_group[3:5]

    return MiscData(
        precipitation_included=precipitation_included,
        is_staffed=is_staffed,
        lowest_cloud=lowest_cloud,
        lowest_cloud_height=lowest_cloud_height,
        visibility=Visibility(visibility),
        original=misc_group,
    )


def build_wind(wind_group, extra_wind_group=None, wind_unit=None):
    """
    Nddff (00fff)
    """
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
        if not data.startswith("29"):  # refer to the manual
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
            name=f"enumerated_group_{group_type}",
            description=f"Invalid group type {group_type}",
        )
    return result


# ==================== CONVERSIONS ====================
def _parse_temperature(data, note=""):
    """Parse temperature data (1sTTT or 2sTTT format)"""
    sign_char = data[0]
    temp_value = data[1:4]

    return TemperatureData(sign_char, temp_value, original=data, note=note)


def _parse_pressure(data):
    """Parse pressure data (PPPP format)"""
    return PressureData(data, original=data)


def _parse_pressure_tendency(data):
    """Parse pressure tendency (appp format)"""
    characteristic_code = data[0]
    characteristic = TENDENCY_MAP.get(characteristic_code)
    value = data[1:4]
    return PressureTendency(characteristic, characteristic_code, value, original=data)


def _parse_precipitation(data):
    """Parse precipitation data (RRRt format)"""
    amount_code = data[0:3]
    duration = data[3]
    duration_description = DURATION_MAP.get(duration)
    return PrecipitationData(amount_code, duration, duration_description, original=data)


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


def build_section_3_group(group_type, data, extra_data=None):
    """
    Build Section 3 groups (333xx groups) according to WMO standard
    """
    # no zero group
    # doesn't handle the mysterious 80000 group (and the extra groups that follow)
    if group_type in {"1", "2"}:  # 1snTxTxTx 2snTnTnTn
        # recycled
        result = _parse_temperature(data, note="max" if group_type == "1" else "min")
    elif group_type == "3":  # 3Ejjj (depends on the regional consensus)
        result = _parse_soil(data)
    elif group_type == "4":  # 4E'sss - Snow depth
        result = _parse_snow_depth(data)
    elif group_type == "5":
        result = _parse_section_3_group_5(data, extra_data)
    elif group_type == "6":  # same as enumerated groups
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


def _parse_soil(data):
    soil = data[0]
    soil_description = SOIL_STATE.get(soil)
    return Soil(soil, soil_description, original=data)


def _parse_snow_depth(data):
    """Parse snow depth group: 4E'sss"""
    ground_state_snow = data[0]  # E'
    snow_depth = data[1:4]  # sss

    return SnowDepthData(
        ground_state_snow,
        GROUND_STATE_SNOW.get(ground_state_snow),
        snow_depth,
        original=data,
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
        original=data,
    )


# section 3 group 5 and friends
def _parse_section_3_group_5(data, extra_data=None):
    """
    Parse section 3 group 5 data according to WMO regulation 12.4.7

    Args:
        data: The main group 5 string (e.g., "55SSS", "553SS", "55407", etc.)
        extra_data: Optional supplementary data (e.g., "4FFFF", "5 F_24 F_24 F_24 F_24")

    Returns:
        Appropriate AST node for the group 5 data
    """
    extra_data = extra_data or []
    if data.startswith("4"):  # 54g0sndT - Temperature change
        return _parse_temperature_change(data[1:])
    elif data.startswith("53"):  # 553SS - Hourly sunshine
        return _parse_sunshine(data[2:], extra_data, "hourly")
    elif data.startswith("54") or data.startswith("55"):  # 55407/55408/55507/55508
        return _parse_radiation(
            data, extra_data, "hourly" if data.startswith("54") else "daily"
        )
    elif data.startswith("5"):  # 55SSS - Daily sunshine
        return _parse_sunshine(data[1:], extra_data)
    elif data.startswith("6"):  # 56 D_L D_M D_H - Cloud direction/drift
        return _parse_cloud_direction(data[1:])
    elif data.startswith("7"):  # 57 C D_a e_c - Cloud direction/elevation
        return _parse_cloud_elevation(data)
    elif data.startswith("8"):  # 58 p_24 p_24 p_24 - Positive pressure change
        return _parse_pressure_change(data, 1)
    elif data.startswith("9"):  # 59 p_24 p_24 p_24 - Negative pressure change
        return _parse_pressure_change(data, -1)
    # 5EEEiE - Evaporation/evapotranspiration
    return _parse_evaporation(data)


def _parse_evaporation(data):
    """Parse 5 E E E i_E - Evaporation/evapotranspiration"""
    evaporation_mm = data[:3]  # EEE
    indicator = EVAPORATION_CODES.get(data[3])  # i_E

    return Evaporation(
        evaporation_mm=evaporation_mm, indicator=indicator, original=data
    )


def _parse_temperature_change(data):
    """Parse 54 g_0 s_n d_T - Temperature change"""
    # hours
    # 0-5
    period = data[0]  # p 213 WMO manual
    # 3845
    # -1 1 or 9 (:2)
    sign = data[1]
    temperature_change = TEMPERATURE_CHANGE.get(data[2])

    return TemperatureChange(period, sign, temperature_change)


def _parse_sunshine(data, extra_data, type_="daily"):
    """Parse 55SSS/553SS - Daily/Hourly sunshine duration"""
    # obviously, 3XX values for SSS are invalid
    # > 240 is technically valid, though
    duration = data[: 3 if type_ == "daily" else 2]  # SSS/SS

    radiation_data = [_parse_radiation_supplementary(extra, type_) for extra in extra_data]

    return SunshineDuration(
        duration_type=type_,
        duration_hours=duration,
        radiation_data=radiation_data,
        original=data,
    )


def _parse_radiation(data, extra_data, type_="daily"):
    """Parse 55507/55508 / 55407/55408 - Radiation"""
    radiation_type, description, unit = SPECIAL_RADIATION_TYPES.get(data)
    value = [_parse_radiation_supplementary(extra, type_) for extra in extra_data]

    return Radiation(
        radiation_type=radiation_type,
        radiation_type_description=description,
        period=type_,
        value=value,
        unit=unit,
        original=data,
    )


def _parse_cloud_direction(data):
    """Parse 56 D_L D_M D_H - Cloud direction and drift"""
    dirs = []
    for i in range(3):
        d = data[i]
        dirs.append(d)
        if d in {"0", "9"}:
            dirs.append(SPECIAL_DIRECTION["clouds"].get(d))
        else:
            dirs.append(DIRECTION.get(d))
    return CloudDirection(*dirs, original=data)


def _parse_cloud_elevation(data):
    """Parse 57C D_a e_c - Cloud direction and elevation"""
    cloud = data[0]
    direction = data[1]
    cloud_description = CLOUD_TYPES.get(cloud)
    if direction in {"0", "9"}:
        direction_description = SPECIAL_DIRECTION["phenomena"].get(direction)
    else:
        direction_description = DIRECTION.get(direction)

    return CloudElevation(
        cloud, cloud_description, direction, direction_description, original=data
    )


def _parse_pressure_change(data, sign):
    """Parse (58|59)p_24 p_24 p_24 - Pressure change"""
    pressure_change = data

    return PressureChange(sign=sign, pressure_change=pressure_change, original=data)


def _parse_radiation_supplementary(data, period):
    """Parse radiation value from FFFF or F_24 F_24 F_24 F_24"""
    radiation_code = data[0]
    if period == "daily":
        radiation_type, radiation_type_description, unit = RADIATION_TYPES_DAILY.get(
            radiation_code, (None, None, None)
        )
    else:
        radiation_type, radiation_type_description, unit = RADIATION_TYPES_HOURLY.get(
            radiation_code, (None, None, None)
        )
    value = data[1:]

    return RadiationData(
        radiation_code,
        radiation_type,
        radiation_type_description,
        value,
        unit,
        original=data,
    )


# section 3 group 9
def _parse_special_phenomena(data):
    """Parse special phenomena group: 9 S_p S_p s_p s_p"""
    # TABLE 3778
    # 100 cases, each one with a different way of
    # interpreting s_p s_p based on S_p S_p
    return Metadata(
        {"original": data}, name="special_phenomena"
    )
