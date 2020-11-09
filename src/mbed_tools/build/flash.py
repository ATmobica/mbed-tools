#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Flash binary onto the connected device."""

import shutil
import os
import pathlib
import platform

from mbed_tools.devices.device import Device
from mbed_tools.devices.devices import get_connected_devices
from mbed_tools.build.exceptions import BinaryFileNotFoundError, DeviceNotFoundError


def _flash_dev(disk: pathlib.Path, image_path: pathlib.Path) -> None:
    """Flash device using copy method.

    Args:
        disk: Device mount point.
        image_path: Image file to be copied to device.
    """
    shutil.copy(image_path, disk, follow_symlinks=False)
    if not platform.system() == "Windows":
        os.sync()


def _find_connected_device(mbed_target: str) -> Device:
    """Check if requested device is connected to the system.

    Look through the devices connected to the system and if a requested device is found then return it.

    Args:
       mbed_target: The name of the Mbed target to build for.

    Returns:
        Device if requested device is connected to system.

    Raises:
        DeviceNotFoundError: the requested board is not connected to the system
    """
    connected_devices = get_connected_devices()
    for device in connected_devices.identified_devices:
        if device.mbed_board.board_type.upper() == mbed_target.upper():
            return device

    raise DeviceNotFoundError("The target board you compiled for is not connected to your system.")


def _build_binary_file_path(program_path: pathlib.Path, build_dir: pathlib.Path, hex_file: bool) -> pathlib.Path:
    """Build binary file name.

    Args:
       program_path: Path to the Mbed project.
       build_dir: Path to the CMake build folder.
       hex_file: Use hex file.

    Returns:
        Path to binary file.

    Raises:
        BinaryFileNotFoundError: binary file not found in the path specified
    """
    fw_fbase = build_dir / program_path.name
    fw_file = fw_fbase.with_suffix(".hex" if hex_file else ".bin")
    if not fw_file.exists():
        raise BinaryFileNotFoundError(f"Build program file (firmware) not found {fw_file}")
    return fw_file


def flash_binary(program_path: pathlib.Path, build_dir: pathlib.Path, mbed_target: str, hex_file: bool) -> None:
    """Flash binary onto a device.

    Look through the connected devices and flash the binary if the connected and built target matches.

    Args:
       program_path: Path to the Mbed project.
       build_dir: Path to the CMake build folder.
       mbed_target: The name of the Mbed target to build for.
       hex_file: Use hex file.
    """
    device = _find_connected_device(mbed_target)
    fw_file = _build_binary_file_path(program_path, build_dir, hex_file)
    _flash_dev(device.mount_points[0].resolve(), fw_file)