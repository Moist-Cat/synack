import unittest
import json
import os
import warnings
from pathlib import Path
from typing import Dict, Any, Optional

from synack.parser import SYNOPParser

BASE_DIR = Path(__file__).parent

class TestSynopParser(unittest.TestCase):
    """Test suite for SYNOP (FM-12) message parser"""
    
    # Configuration
    TEST_DATA_DIR = BASE_DIR / "test_data"  # Root directory for test data
    RAW_EXTENSION = ".synop"       # Extension for raw message files
    JSON_EXTENSION = ".json"     # Extension for expected JSON files
    
    def run_synop_test(self, raw_file_path: Path, json_file_path: Optional[Path] = None):
        """
        Run a single SYNOP test case
        
        Args:
            raw_file_path: Path to the raw message file
            json_file_path: Path to the expected JSON file (optional)
        """
        # Read raw message
        with open(raw_file_path, 'r', encoding='ascii', errors="ignore") as f:
            raw_message = f.read().strip()
        
        try:
            # Parse the message
            decoded_result = SYNOPParser().parse(raw_message)
            
            if json_file_path and json_file_path.exists():
                # Load expected result and compare
                with open(json_file_path, 'r', encoding='ascii', errors="ignore") as f:
                    expected_result = json.load(f)
                
                # Compare the results
                self.assertEqual(
                    # avoid errors related to JSON compliance
                    # e.g. (a, b, c) -> [a, b, c]
                    json.loads(json.dumps(decoded_result["message"], default=str)),
                    expected_result,
                    f"Parsed result doesn't match expected for {raw_file_path}"
                )
            else:
                # No JSON file exists - show warning and dump decoded result
                warnings.warn(
                    f"No expected JSON file found for {raw_file_path}. "
                    f"Parsed result (no errors):\n{json.dumps(decoded_result, indent=2)}",
                    UserWarning
                )
                # Test passes if no parsing errors occurred
                self.assertTrue(decoded_result is not None)
                
        except Exception as e:
            if json_file_path and json_file_path.exists():
                # If JSON exists but parsing failed, re-raise the exception
                raise
            else:
                # If no JSON exists and parsing failed, still show warning with error
                warnings.warn(
                    f"No expected JSON file found for {raw_file_path}. "
                    f"Parsing failed with error: {str(e)}",
                    UserWarning
                )
                # Test fails because parsing errored
                self.fail(f"Parsing failed for {raw_file_path}: {str(e)}")

    @classmethod
    def create_test_methods(cls):
        """Dynamically create test methods for all test files"""
        test_data_dir = Path(cls.TEST_DATA_DIR)
        
        if not test_data_dir.exists():
            warnings.warn(f"Test data directory '{cls.TEST_DATA_DIR}' not found")
            return
        
        # Walk through all directories and find raw message files
        for raw_file_path in test_data_dir.rglob(f"*{cls.RAW_EXTENSION}"):
            # Determine the corresponding JSON file path
            json_file_path = raw_file_path.with_suffix(cls.JSON_EXTENSION)
            
            # Generate test method name from file path
            rel_path = raw_file_path.relative_to(test_data_dir)
            test_name = f"test_{rel_path.with_suffix('')}"
            # Replace non-alphanumeric characters with underscores
            test_name = "".join(c if c.isalnum() else "_" for c in test_name)
            
            # Create the test method
            test_method = cls._create_test_method(raw_file_path, json_file_path)
            
            # Add the test method to the class
            setattr(cls, test_name, test_method)
    
    @classmethod
    def _create_test_method(cls, raw_file_path: Path, json_file_path: Path):
        """Create a test method for a specific test case"""
        
        def test_method(self):
            self.run_synop_test(raw_file_path, json_file_path)
        
        # Add a docstring for better test reporting
        test_method.__doc__ = f"Test SYNOP parsing for {raw_file_path.relative_to(Path(cls.TEST_DATA_DIR))}"
        
        return test_method


def generate_all_missing_json(cls):
    """Generate JSON files for all raw messages that don't have expected results"""
    test_dir = Path(cls.TEST_DATA_DIR)
    
    for raw_file in test_dir.rglob(f"*{cls.RAW_EXTENSION}"):
        json_file = raw_file.with_suffix(f'{cls.JSON_EXTENSION}')
        
        if not json_file.exists():
            print(f"Generating JSON for: {raw_file}")
            
            with open(raw_file, 'r', encoding='ascii', errors="ignore") as f:
                raw_message = f.read().strip()
            
            try:
                decoded_result = SYNOPParser().parse(raw_message)
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(decoded_result["message"], f, indent=2, ensure_ascii=False, default=str)
                
                print(f"  -> Created: {json_file}")
                
            except Exception as e:
                print(f"  -> Failed: {e}")

# Create dynamic test methods when the class is defined
TestSynopParser.create_test_methods()

def run_tests():
    """Run the test suite with additional configuration"""
    generate_all_missing_json(TestSynopParser)
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
