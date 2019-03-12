"""
    Fixtures for updateControl
"""

import pytest
import os
import time

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'


@pytest.fixture()
def clean_test(target, legato, tmpdir):
    """
    Fixture to clean up legato after the test

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation

    """

    os.chdir(str(tmpdir))
    yield

    time.sleep(60)
    legato.restore_golden_legato()


@pytest.fixture()
def init_update(target, read_config):
    """
    Get values from upgrade.xml

    Args:
        target: fixture to communicate with the target
        read_config: fixture to get value from .xml file

    """

    update_cfg = {}

    fw_path = read_config.findtext("upgrade/current_firmware_path")
    fw_pkg = read_config.findtext("upgrade/current_firmware_package")
    yoc_path = read_config.findtext("upgrade/current_yocto_path")
    yoc_pkg = read_config.findtext("upgrade/current_yocto_package")
    legato_path = read_config.findtext("upgrade/current_legato_path")
    legato_pkg = read_config.findtext("upgrade/current_legato_package")

    # Current:
    update_cfg["CURRENT_FIRMWARE_PATH"] = fw_path
    update_cfg["CURRENT_FIRMWARE_PACKAGE"] = fw_pkg

    update_cfg["CURRENT_YOCTO_PATH"] = yoc_path
    update_cfg["CURRENT_YOCTO_PACKAGE"] = yoc_pkg

    update_cfg["CURRENT_LEGATO_PATH"] = legato_path
    update_cfg["CURRENT_LEGATO_PACKAGE"] = legato_pkg

    yield update_cfg