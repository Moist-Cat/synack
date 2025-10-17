"""
Module in charge of defining and constructing AST nodes
"""

from abc import ABC, abstractmethod
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
import warnings

PASCAL_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def get_name(obj):
    return re.sub(PASCAL_PATTERN, "_", obj.__class__.__name__).lower()


# ==================== BASE AST NODES ====================
class ASTNode(ABC):
    original: str = ""
    errors: List[str] = None

    def __init__(self, original="", errors=None):
        self.original = original
        self.errors = [] or errors

    def __setattr__(self, name, value):
        """
        Any attribute can be missable (that is "/").
        We perform conversions here.
        """
        # heuristics to determine if we should automatically
        # conver the type
        if (
            name in self.__annotations__
            and isinstance(value, str)
            and not name.startswith("_")
            and not name in {"original", "errors"}
        ):
            data_type = self.__annotations__[name]
            if "/" not in value:
                try:
                    value = data_type(value)
                except ValueError:
                    value = None
            elif data_type is not str:
                warnings.warn(f"%s is missing and can not be converted" % (value))
                value = None

            if value is not None and hasattr(self, f"convert_{name}"):
                value = getattr(self, f"convert_{name}")(value)
        super().__setattr__(name, value)

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate(self) -> List[str]:
        pass


class ErrorNode(ASTNode):
    field: str = ""
    description: str = ""
    name: str = ""

    def __init__(self, name="", field="", description=""):
        super().__init__()
        self.field = field
        self.description = description
        self.name = name

    def to_dict(self):
        return {"field": self.field, "description": self.description}

    def validate(self):
        return []


# ==================== METADATA NODES ====================


@dataclass
class StationInfo(ASTNode):
    station_id: str
    message_type: str
    station_type: str
    block_number: str
    station_number: str
    original_message_type: str = ""
    original_station_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "station_id": self.station_id,
            "message_type": self.message_type,
            "station_type": self.station_type,
            "block_number": self.block_number,
            "station_number": self.station_number,
            "original_message_type": self.original_message_type,
            "original_station_id": self.original_station_id,
        }

    def validate(self) -> List[str]:
        errors = []
        if self.message_type not in ["AAXX", "BBXX", "OOXX"]:
            errors.append(f"Invalid message type: {self.message_type}")
        return errors


@dataclass
class DateLocation(ASTNode):
    day: int
    hour: int
    wind_indicator: str
    wind_units: str
    original: str
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "hour": self.hour,
            "wind_indicator": self.wind_indicator,
            "wind_units": self.wind_units,
            "original": self.original,
        }

    def validate(self) -> List[str]:
        errors = []
        if not (1 <= self.day <= 31):
            errors.append(f"Invalid day: {self.day}")
        if not (0 <= self.hour <= 23):
            errors.append(f"Invalid hour: {self.hour}")
        return errors


@dataclass
class Metadata(ASTNode):
    def __init__(self, *args, name=""):
        super().__init__()
        self.fields = list(args)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        res = {}
        for cls in self.fields:
            k = cls.name if hasattr(cls, "name") and cls.name else get_name(cls)
            if not isinstance(cls, dict):
                if not isinstance(cls, ASTNode):
                    v = cls
                else:
                    v = cls.to_dict()
            else:
                if set(cls.keys()).intersection(res.keys()):
                    warnings.warn(
                        "{cls} and {res} contain common keys. Can not merge metadata"
                    )
                else:
                    res.update(cls)
                continue
            if k in res:
                warnings.warn(
                    f"{k} is already in {self.name}. Either rename it or use another class"
                )
            res[k] = v
        return res

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def validate(self) -> List[str]:
        validation_errors = []
        for fld in self.fields:
            validation_errors.extend(fld.validate())

    def add(self, fld):
        # keep order
        self.fields.insert(0, fld)

    def __str__(self):
        return f"<Metadata({self.name=})>"

    __repr__ = __str__


# ==================== WEATHER DATA NODES ====================


@dataclass
class MiscData(ASTNode):
    precipitation_included: bool
    is_staffed: bool
    lowest_cloud: str
    visibility: "Visibility"
    original: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "precipitation_included": self.precipitation_included,
            "is_staffed": self.is_staffed,
            "lowest_cloud": self.lowest_cloud,
            "visibility": self.visibility.to_dict(),
            "original": self.original,
        }

    def validate(self) -> List[str]:
        return []


DIRECTIONS = [
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


@dataclass
class WindDirection(ASTNode):
    degrees: int

    def convert_degrees(self, value):
        return value * 10

    def convert_direction(self, value):
        if self.degrees is None:
            return value
        compass_idx = round(self.degrees / 22.5) % 16
        return DIRECTIONS[compass_idx]

    def to_dict(self):
        return {
            "degrees": self.degrees,
            "direction": self.convert_direction(self.degrees),
        }

    def validate(self):
        return []


@dataclass
class WindSpeed(ASTNode):
    speed: int
    unit: str = "m/s"

    def convert_degrees(self, value):
        return value * 10

    def convert_direction(self, value):
        if self.degrees is None:
            return value
        compass_idx = round(self.degrees / 22.5) % 16
        return DIRECTIONS[compass_ids]

    def to_dict(self):
        return {
            "speed": self.speed,
            "unit": self.unit,
        }

    def validate(self):
        return []


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


@dataclass
class Visibility(ASTNode):
    value: int
    unit: str = "km"

    def convert_value(self, code):
        if code <= 50:
            value = code / 10
        elif code <= 55:
            # not used
            value = None
        elif code <= 80:
            value = code - 50
            value = None
        elif code <= 89:
            value = 30 + (code - 80) * 5
        else:
            value = SPECIAL_VISIBILITY.get(code)
        return value

    def convert_direction(self, value):
        if self.degrees is None:
            return value
        compass_idx = round(self.degrees / 22.5) % 16
        return DIRECTIONS[compass_ids]

    def to_dict(self):
        return {
            "value": self.value,
            "unit": self.unit,
        }

    def validate(self):
        return []


@dataclass
class WindData(ASTNode):
    ship_id: Optional[str]
    cloud_cover: str
    wind_direction: WindDirection
    wind_speed: WindSpeed
    original: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ship_id": self.ship_id,
            "cloud_cover": self.cloud_cover,
            "wind_direction": self.wind_direction.to_dict(),
            "wind_speed": self.wind_speed.to_dict(),
            "original": self.original,
        }

    def validate(self) -> List[str]:
        errors = []
        if self.wind_speed_ms and self.wind_speed_ms > 100:
            errors.append(f"Unrealistic wind speed: {self.wind_speed_ms} m/s")
        return errors


@dataclass
class TemperatureData(ASTNode):
    value: float
    sign: int = 1
    original: str = ""
    unit: str = "celsius"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sign": self.sign,
            "value": self.value,
            "unit": self.unit,
            "original": self.original,
        }

    def convert_value(self, value):
        if self.sign is None:
            return self.value / 10
        return self.sign * (value / 10)

    def validate(self) -> List[str]:
        errors = []
        if self.value and not (-80 <= self.value <= 60):
            errors.append(f"Unrealistic temperature: {self.value}°C")
        return errors


@dataclass
class PressureData(ASTNode):
    value: float
    unit: str = "hPa"
    original: str = ""
    name: str = ""

    def convert_value(self, value):
        value = value / 10
        if value > 99.9:
            return value
        else:
            return value + 1000

    def to_dict(self):
        return {
            "value": self.value,
            "unit": self.unit,
            "original": self.original,
        }

    def validate(self) -> List[str]:
        errors = []
        if self.value and not (870 <= self.value <= 1080):
            errors.append(f"Unrealistic pressure: {self.value} hPa")
        return errors


@dataclass
class PressureTendency(ASTNode):
    characteristic: str
    characteristic_code: str
    value: int
    unit: str = "hPa"
    original: str = ""

    def convert_value(self, value):
        return value / 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "characteristic": self.characteristic,
            "characteristic_code": self.characteristic_code,
            "amount": self.value,
            "units": self.unit,
            "original": self.original,
        }

    def validate(self) -> List[str]:
        return []


@dataclass
class PrecipitationData(ASTNode):
    amount: float
    duration: str
    duration_code: str
    unit: str = "mm"
    original: str = ""

    def validate_amount(self, value):
        if value == 0 or value == 990:
            return 0.0
        else:
            return value / 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "units": "mm",
            "duration": self.duration,
            "duration_code": self.duration_code,
            "original": self.original,
        }

    def validate(self) -> List[str]:
        return []


@dataclass
class WeatherCode(ASTNode):
    code: int
    description: str
    weather_type: str
    name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "description": self.description,
            "type": self.weather_type,
        }

    def validate(self) -> List[str]:
        return []


@dataclass
class CloudType(ASTNode):
    code: str
    description: str
    level: str

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "description": self.description, "level": self.level}

    def validate(self) -> List[str]:
        return []


@dataclass
class ObservationTime(ASTNode):
    hour: int
    minute: int
    original: str

    def to_dict(self) -> Dict[str, Any]:
        return {"hour": self.hour, "minute": self.minute, "original": self.original}

    def validate(self) -> List[str]:
        errors = []
        if self.hour is not None and not (0 <= self.hour <= 23):
            errors.append(f"Invalid observation hour: {self.hour}")
        if self.minute is not None and not (0 <= self.minute <= 59):
            errors.append(f"Invalid observation minute: {self.minute}")
        return errors
