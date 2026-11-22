"""Test environment configuration.

This file is loaded before pytest imports test modules.
"""

import os

os.environ["CAPSTONE_TESTING"] = "1"
