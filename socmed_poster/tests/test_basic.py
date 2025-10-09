"""
Basic tests for the SocMed Poster application.
"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBasicFunctionality(unittest.TestCase):
    """Test basic application functionality."""
    
    def test_import_app(self):
        """Test that we can import the main application."""
        try:
            from socmed_poster import create_app
            app = create_app()
            self.assertIsNotNone(app)
        except ImportError as e:
            self.fail(f"Failed to import create_app: {e}")
    
    def test_diagnose_import(self):
        """Test that we can import the diagnose module."""
        try:
            import diagnose
            self.assertTrue(hasattr(diagnose, '__file__'))
        except ImportError as e:
            self.fail(f"Failed to import diagnose: {e}")

if __name__ == '__main__':
    unittest.main()