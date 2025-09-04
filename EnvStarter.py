#!/usr/bin/env python3
"""
EnvStarter - Start your perfect work environment with one click.
Main executable script.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the main application
from src.envstarter.main import main

if __name__ == "__main__":
    main()