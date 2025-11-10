import json
import ply.lex as lex
import ply.yacc as yacc
import re
from datetime import datetime, timedelta
import traceback

from synack.builder import (
    build_station_info,
    build_date_location,
    build_misc,
    build_wind,
    build_enumerated_group,
    build_section_3_group,
)
from synack.tree import (
    Metadata,
    ErrorNode,
)

__version__ = "0.2.1"


class SYNOPParser:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.errors = []
        self.build_lexer()
        self.build_parser()

        # Add this to semantic analysis when we implement it
        self.units = {}

    # ==================== LEXER DEFINITION ====================

    # Token list
    tokens = (
        "DIGITS",
        "LETTERS",
        "EQUALS",
        "WHITESPACE",
        "ZERO_CHUNK",
        "DELIMITER_2",
        "DELIMITER_3",
        "DELIMITER_4",
        "DELIMITER_5",
    )

    # Token regex patterns
    t_LETTERS = r"AAXX|BBXX"
    t_WHITESPACE = r"\s+"

    # Ignore whitespace
    t_ignore = " \t"

    t_EQUALS = "="

    t_DELIMITER_2 = "222"
    t_DELIMITER_3 = "333"
    t_DELIMITER_4 = "444"
    t_DELIMITER_5 = "555"

    def t_ZERO_CHUNK(self, t):
        r"00[0-9\/]{1,3}"
        return t

    def t_DIGITS(self, t):
        r"[0-9\/]{4,6}"
        # t.value.replace("\/", "0")
        return t

    def t_error(self, t):
        self.errors.append(
            f"Lexer error: Illegal character '{t.value[0]}' at position {t.lexpos}"
        )
        t.lexer.skip(1)

    def build_lexer(self):
        self.lexer = lex.lex(module=self)

    # ==================== PARSER DEFINITION ====================

    def p_synop_message(self, p):
        """
        synop_message : section_0 section_1 EQUALS
                      | section_0 section_1 section_3 EQUALS
                      | section_0 section_1
                      | section_0 section_1 section_3
        """
        if len(p) > 3:
            p[0] = Metadata(p[1], p[2], p[3], name="main")
        elif len(p) > 2:
            p[0] = Metadata(p[1], p[2], name="main")
        else:
            p[0] = Metadata(p[1], name="main")
        p[0] = p[0].to_dict()

    # Section 0: Message Type (AAXX/BBXX)
    # Location and Time (YYGGi IIiii or YYGGiw IIiii for ships)
    def p_section_0(self, p):
        """section_0 : LETTERS DIGITS DIGITS"""
        message_type = p[1]
        date_group = p[2]  # YYGGi
        station_group = p[3]  # IIiii

        station_data = build_station_info(message_type, station_group)

        if len(date_group) < 5:
            msg = f"Invalid date/time group: {date_group}"
            self.errors.append(msg)
            day = hour = 0
            wind_indicator = "/"
            date_data = ErrorNode(field="date_data", description=msg)
        else:
            date_data = build_date_location(date_group)

        # NOTE lookbehind
        self.units["wind"] = (
            date_data.wind_units if hasattr(date_data, "wind_units") else None
        )

        p[0] = Metadata(date_data, station_data, name="section_0")

    # Section I: Wind and Visibility and clouds iRiXhVV (iiiNddff or Nddff) (00fff)
    # and enumerated groups ([0-9][0-9]{4}...)
    def p_section_1(self, p):
        """
        section_1 : wind_visibility_clouds temperature_pressure_groups
        """
        p[0] = Metadata(
            p[1],
            p[2],
            name="section_1",
        )

    # Nddff and 00fff
    def p_wind_visibility_clouds(self, p):
        """
        wind_visibility_clouds : DIGITS DIGITS ZERO_CHUNK
                               | DIGITS DIGITS
                               | DIGITS ZERO_CHUNK
                               | DIGITS
        """
        # the last case, DIGITS ZERO_CHUNK, can happen in rare cases
        # where Nd are both 0
        group_misc = p[1]
        group_wind = p[2] if len(p) >= 3 else None
        extra_group = p[3] if len(p) == 4 else None

        if len(group_misc) != 5:
            msg = f"Invalid misc group: {group_misc}"
            self.errors.append(msg)
            group_misc_data = ErrorNode(field="misc_group", description=msg)
        else:
            group_misc_data = build_misc(group_misc)

        if not group_wind or len(group_wind) not in {5, 6}:
            msg = f"Invalid wind/visibility group: {group_wind}"
            self.errors.append(msg)
            group_wind_data = ErrorNode(field="wind_group")
        else:
            group_wind_data = build_wind(
                group_wind, extra_group, wind_unit=self.units["wind"]
            )

        p[0] = Metadata(group_misc_data, group_wind_data, name="wind_visibility_clouds")

    def p_temperature_pressure_groups(self, p):
        """
        temperature_pressure_groups : temperature_pressure_group temperature_pressure_groups
                                    | temperature_pressure_group
        """
        if len(p) == 2:
            p[0] = Metadata(p[1], name="enumerated_groups")
        else:
            p[2].add(p[1])
            p[0] = p[2]

    def p_temperature_pressure_group(self, p):
        """
        temperature_pressure_group : DIGITS
        """
        group = p[1]
        group_type = group[0]
        data = group[1:]

        if len(group) < 4:
            msg = f"Invalid temperature/pressure group: {group}"
            self.errors.append(msg)
            group_enumerated = ErrorNode(field=f"enumerated_group_{group_type}", description=msg)
        else:
            group_enumerated = build_enumerated_group(group_type, data)
        p[0] = group_enumerated

    def p_section_3(self, p):
        """
        section_3 : DELIMITER_3 section_3_groups
        """
        p[0] = Metadata(p[2], name="section_3")

    def p_section_3_groups(self, p):
        """
        section_3_groups : section_3_group section_3_groups
                         | section_3_group
        """
        if len(p) == 2:
            p[0] = Metadata(p[1], name="section_3_groups")
        else:
            p[2].add(p[1])
            p[0] = p[2]

    def p_section_3_group(self, p):
        """
        section_3_group : DIGITS
        """
        group = p[1]
        group_type = group[0]
        data = group[1:]
        if len(data) < 4:
            msg = f"Invalid section 3 group: {group}"
            self.errors.append(msg)
            decoded_group = ErrorNode(field=f"section_3_group_{group_type}", description=msg)
        else:
            decoded_group = build_section_3_group(group_type, data)
        p[0] = decoded_group

    # ==================== PUBLIC INTERFACE ====================

    def parse(self, synop_message):
        """
        Parse a SYNOP message and return structured data

        Args:
            synop_message (str): Raw SYNOP message string

        Returns:
            dict: Structured weather data with original codes and interpretations
        """
        # Reset errors for new parse
        self.errors = []

        # Clean the input message
        clean_message = self._clean_synop_message(synop_message)

        try:
            result = self.parser.parse(clean_message, lexer=self.lexer)
            if not result:
                result = {}
            return {"errors": self.errors.copy(), "message": result}
        except Exception as e:
            self.errors.extend(traceback.format_exception(e))
            self.errors.append(f"Parser error: {str(e)}")
            return {"errors": self.errors, "message": synop_message}

    def parse_as_json(self, synop_message):
        return json.dumps(self.parse(synop_message), indent=2, default=str)

    def p_section_1_error(self, p):
        """
        section_1 : error temperature_pressure_groups
        """
        # we know nothing about what was back there
        p[1] = {"wind_visibility_clouds": None}
        self.p_section_1(p)

    def p_synop_message_error(self, p):
        """
        synop_message : section_0 section_1 error EQUALS
                      | section_0 section_1 error
                      | section_0 error EQUALS
                      | section_0 error
        """
        self.errors.append(
            "Found an error at the end of the statement (probably an unimplemented section). Resynchronizing..."
        )
        self.p_synop_message(p)

    def p_error(self, p):
        if p:
            self.errors.append(
                f"Syntax error at token '{p.value}' (type: {p.type}) at position {p.lexpos}"
            )
            # discard
            self.parser.errok()
        else:
            self.errors.append(
                "Syntax error at EOF (probably due to a missing `=` character)"
            )

    def build_parser(self):
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)

    # ==================== VALUE PARSING METHODS ====================

    def _clean_synop_message(self, message):
        """Clean and preprocess the SYNOP message"""
        # Remove multiple spaces, clean up formatting
        message = re.sub(r"\s+", " ", message.strip())
        return message


# ==================== USAGE EXAMPLE ====================


def main():
    """Example usage of the SYNOP parser"""
    parser = SYNOPParser()

    # Example SYNOP message from the requirements
    msgs = [
        "AAXX 01004 88889 12782 61506 10094 20047 30111 40197 53007 60001 70102 81541=",
    ]
    for synop_message in msgs:

        result = parser.parse(synop_message)

        # Print results in a readable format
        import json

        print("SYNOP Parser Results:")
        print("=" * 50)
        print(json.dumps(result, indent=2, default=str))

        if result["errors"]:
            print(f"\nErrors encountered: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"  - {error}")


if __name__ == "__main__":
    main()
