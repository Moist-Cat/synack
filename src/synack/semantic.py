class SYNOPAnalyzer:
    """Performs semantic analysis and unit conversions on the AST"""

    @staticmethod
    def analyze(ast: SYNOPAST) -> SYNOPAST:
        """Perform semantic analysis on the AST"""
        analyzer = SYNOPAnalyzer()
        analyzer._check_consistency(ast)
        analyzer._convert_units(ast)
        analyzer._validate_physical_limits(ast)
        return ast

    def _check_consistency(self, ast: SYNOPAST):
        """Check consistency between different parts of the message"""
        # Check wind speed units consistency
        wind_units = ast.metadata.date_location.wind_units
        wind_data = ast.common_data.wind_visibility_clouds.wind_cloud

        if wind_units == WindUnits.NOT_MEASURED and wind_data.wind_speed_ms is not None:
            ast.errors.append("Wind speed reported but units indicate not measured")

    def _convert_units(self, ast: SYNOPAST):
        """Ensure all units are converted to standard units"""
        # Wind speeds are already converted during AST construction
        # Temperatures are already in Celsius
        # Pressures are already in hPa
        pass

    def _validate_physical_limits(self, ast: SYNOPAST):
        """Validate that all values are within physical limits"""
        # This is now handled by the individual node validate() methods
        pass
