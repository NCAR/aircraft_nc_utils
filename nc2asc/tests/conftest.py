"""
Pytest configuration and fixtures for nc2asc tests.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def sample_config_dict():
    """Return a sample configuration dictionary."""
    return {
        "header": {
            "pi_name": "Test PI",
            "pi_organization": "Test Organization",
            "datasource_desc": "Test Instruments on",
            "data_interval": 1.0,
            "missing_value": -99999.0
        },
        "normal_comments": {
            "pi_contact_info": "test@example.com",
            "platform": "NSF/NCAR {platform} {tail_number}",
            "location": "Test location",
            "associated_data": "Test data",
            "instrument_info": "Test instruments",
            "data_info": "Test info",
            "uncertainty": "Test uncertainty",
            "ulod_flag": "-77777",
            "ulod_value": "N/A",
            "llod_flag": "-88888",
            "llod_value": "N/A",
            "dm_contact_info": "Test DM",
            "project_info": "Test Project",
            "stipulations_on_use": "Test stipulations",
            "other_comments": "none",
            "revision": "RA",
            "revision_comments": {
                "RA": "Field Data",
                "RB": "Test revision"
            }
        },
        "special_comments": [],
        "platform_mapping": {
            "N677F": "GV",
            "N130AR": "C130"
        }
    }


@pytest.fixture
def sample_batch_content():
    """Return sample batch file content."""
    return """
hd=ICARTT
dt=NoDate
tm=SecOfDay
sp=comma
fv=-99999
version=RA
avg=10
ti=50000,70000
Vars=LATC
Vars=LONC
Vars=ALTX
"""
