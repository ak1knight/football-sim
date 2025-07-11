"""
Unit tests for the football simulation engine.

This module contains test cases for all major components of the simulation.
"""

import unittest
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_models import TestPlayer, TestTeam
from tests.test_simulation import TestGameEngine
from tests.test_api import TestSimulationAPI, TestTeamAPI

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestPlayer))
    test_suite.addTest(unittest.makeSuite(TestTeam))
    test_suite.addTest(unittest.makeSuite(TestGameEngine))
    test_suite.addTest(unittest.makeSuite(TestSimulationAPI))
    test_suite.addTest(unittest.makeSuite(TestTeamAPI))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
