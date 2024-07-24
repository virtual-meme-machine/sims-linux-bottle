#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
import zipfile

from collections import namedtuple

INPUT_ZIP: str = os.path.abspath(path=os.path.expanduser(path=sys.argv[1])) if len(sys.argv) > 1 else None
NOCD_PATCH: str = os.path.join(os.path.dirname(p=os.path.realpath(filename=__file__)), "nocd-patch.bin")

FLATPAK_EXEC: str = "/usr/bin/flatpak"

BOTTLES_IDENTIFIER: str = "com.usebottles.bottles"
BOTTLES_CLI_EXEC: list[str] = [FLATPAK_EXEC, "run", "--command=bottles-cli", BOTTLES_IDENTIFIER]

SIMS_BOTTLE_ID: str = "the-sims-complete"
SIMS_BOTTLE_PATH: str = os.path.expanduser(f"~/.var/app/com.usebottles.bottles/data/bottles/bottles/{SIMS_BOTTLE_ID}")
SIMS_BOTTLE_DRIVE_C: str = os.path.join(SIMS_BOTTLE_PATH, "drive_c")
SIMS_EXEC_PATH: str = os.path.join(SIMS_BOTTLE_DRIVE_C, "The Sims/Sims.exe")
SIMS_ICON_PATH: str = os.path.join(SIMS_BOTTLE_DRIVE_C, "The Sims/00000000.256")
SIMS_GAME_NAME: str = "The Sims - Complete Collection"

RegistryKey = namedtuple(typename="RegistryKey", field_names="value data_type data")
SIMS_REGISTRY_ROOT: str = "HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Maxis\\The Sims"
SIMS_REGISTRY_KEYS: list[RegistryKey] = [
    RegistryKey(value="EP2Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="EP3Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="EP3Patch", data_type="REG_SZ", data=2),
    RegistryKey(value="EP4Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="EP5Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="EP5Patch", data_type="REG_SZ", data=1),
    RegistryKey(value="EP6Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="EP7Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="EP8Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="EPDInstalled", data_type="REG_SZ", data=1),
    RegistryKey(value="EPDPatch", data_type="REG_SZ", data=1),
    RegistryKey(value="EPInstalled", data_type="REG_SZ", data=1),
    RegistryKey(value="Installed", data_type="REG_SZ", data=1),
    RegistryKey(value="InstallPath", data_type="REG_SZ", data="C:\\The Sims"),
    RegistryKey(value="Language", data_type="REG_DWORD", data=1033),
    RegistryKey(value="SIMS_CURRENT_NEIGHBORHOOD_NUM", data_type="REG_SZ", data=1),
    RegistryKey(value="SIMS_CURRENT_NEIGHBORHOOD_PATH", data_type="REG_SZ", data="UserData"),
    RegistryKey(value="SIMS_DATA", data_type="REG_SZ", data="C:\\The Sims"),
    RegistryKey(value="SIMS_GAME_EDITION", data_type="REG_SZ", data=255),
    RegistryKey(value="SIMS_LANGUAGE", data_type="REG_SZ", data="USEnglish"),
    RegistryKey(value="SIMS_SKU", data_type="REG_DWORD", data=1),
    RegistryKey(value="SIMS_SOUND", data_type="REG_SZ", data="C:\\The Sims\\SoundData"),
    RegistryKey(value="TELEPORT", data_type="REG_SZ", data=1),
    RegistryKey(value="Version", data_type="REG_SZ", data=1.2)
]


def add_program(name: str, bottle_id: str, path: str, launch_options: str = ""):
    """
    Registers a program with a Bottle
    :param name: Name of the program, example: "Counter-Strike 1.6"
    :param bottle_id: ID of the program's Bottle
    :param path: Path to the program exec, example: f"{target_root}/Half-Life/hl.exe"
    :param launch_options: Launch options the program should launch with, example: "-game cstrike"
    :return: None
    """
    bottle_programs = subprocess.run(args=BOTTLES_CLI_EXEC + ["programs", "--bottle", bottle_id],
                                     capture_output=True,
                                     check=True).stdout.decode().strip()

    if name in bottle_programs:
        print(f"Program already added to Bottle")
        return

    print(f"Adding '{path}' as a shortcut in Bottle: '{bottle_id}'")
    subprocess.run(args=BOTTLES_CLI_EXEC + ["add",
                                            "--bottle", bottle_id,
                                            "--name", name,
                                            "--path", path,
                                            "--launch-options", launch_options],
                   capture_output=True,
                   check=True)


def create_desktop_file(name: str, bottle_id: str, icon_path: str):
    """
    Creates a .desktop file for a program in a Bottle
    :param name: Name of the program, example: "Counter-Strike 1.6"
    :param bottle_id: ID of the program's Bottle
    :param icon_path: Path to the icon file that should be used, example: "/path/to/my/icon.png"
    :return: None
    """
    desktop_file = os.path.expanduser(path=f"~/.local/share/applications/{bottle_id}.desktop")
    desktop_lines = [
        f"[Desktop Entry]",
        f"Name={name}",
        f"Exec=flatpak run --command=bottles-cli com.usebottles.bottles run -p '{name}' -b '{bottle_id}' -- %u",
        f"Type=Application",
        f"Terminal=false",
        f"Categories=Application;",
        f"Icon={icon_path}",
        f"Comment=Launch {name} using Bottles.",
        f"StartupWMClass={name}",
        f"Actions=Configure;",
        f"[Desktop Action Configure]",
        f"Name=Configure in Bottles",
        f"Exec=flatpak run com.usebottles.bottles -b '{bottle_id}'",
    ]

    if os.path.isfile(path=desktop_file):
        print(f".desktop file already exists")
        return

    print("Creating .desktop file")
    with open(file=desktop_file, mode="w") as desktop_file:
        for line in desktop_lines:
            desktop_file.write(line)
            desktop_file.write("\n")


def add_registry_key(bottle_id: str, key: str, value: str, data_type: str, data: str or int):
    """
    Adds a new key to a Bottle's registry
    :param bottle_id: ID of the Bottle we want to edit the registry for
    :param key: Registry key that we want to add, example: "HKEY_LOCAL_MACHINE\\Software\\ExampleApp\\Data"
    :param value: Registry value that we want to add, example: "ExampleValue"
    :param data_type: Data type for the data we are adding to the registry, see: https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-value-types
    :param data: Data that should be stored at the key/value pair, example: "testing 123"
    :return: None
    """
    print(f"Updating registry: Key: '{key}\\{value}', Value: '{data}'")
    subprocess.run(args=BOTTLES_CLI_EXEC + ["reg", "--bottle", bottle_id, "add",
                                            "--key", key,
                                            "--value", value,
                                            "--data", str(data),
                                            "--key-type", data_type],
                   capture_output=True,
                   check=True)


def setup_bottles():
    """
    Requests the user preform the initial Bottles setup and launched Bottles
    :return: None
    """
    runners = os.path.expanduser(path=f"~/.var/app/{BOTTLES_IDENTIFIER}/data/bottles/runners")
    if not os.path.isdir(s=runners):
        print(f"Bottles has not been setup yet, please click through the initial setup and then exit Bottles")
        subprocess.run(args=["/usr/bin/killall", "bottles"])
        subprocess.run(args=[FLATPAK_EXEC, "run", BOTTLES_IDENTIFIER],
                       capture_output=True,
                       check=True)


def main():
    """
    Installs The Sims into a Bottle (Windows app container) on a Linux host
    :return: None
    """
    # Skip install if game is already installed
    if os.path.isfile(path=SIMS_EXEC_PATH):
        print(f"'{SIMS_GAME_NAME}' appears to be installed already, nothing to do.")
        print(f"Game install path: {os.path.dirname(p=SIMS_EXEC_PATH)}")
        exit(255)

    # Check if user provided game data zip
    if INPUT_ZIP is None or not os.path.isfile(path=INPUT_ZIP):
        print(f"'{SIMS_GAME_NAME}' game data .zip file was not provided or is not a file, aborting installation.")
        print(f"Usage: {sys.argv[0]} 'path/to/sims_game_data.zip'")
        exit(1)

    # Setup Bottles if needed
    setup_bottles()

    # Create game Bottle
    print(f"Creating new Bottle: '{SIMS_BOTTLE_ID}'")
    subprocess.run(args=BOTTLES_CLI_EXEC + ["new",
                                            "--bottle-name", SIMS_BOTTLE_ID,
                                            "--environment", "gaming"],
                   capture_output=True,
                   check=True)

    # Extract game data
    print(f"Extracting game data from zip file: '{INPUT_ZIP}'")
    zip_path = os.path.join(SIMS_BOTTLE_DRIVE_C, os.path.basename(p=INPUT_ZIP))
    os.makedirs(name=SIMS_BOTTLE_DRIVE_C, exist_ok=True)
    shutil.copy2(src=INPUT_ZIP, dst=zip_path)
    with zipfile.ZipFile(file=zip_path, mode="r") as data_zip:
        data_zip.extractall(path=SIMS_BOTTLE_DRIVE_C)

    # Apply registry keys
    for reg_key in SIMS_REGISTRY_KEYS:
        add_registry_key(bottle_id=SIMS_BOTTLE_ID,
                         key=SIMS_REGISTRY_ROOT,
                         value=reg_key.value,
                         data_type=reg_key.data_type,
                         data=reg_key.data)

    # Apply no-cd patch
    print("Applying no-cd patch")
    shutil.move(src=SIMS_EXEC_PATH, dst=f"{SIMS_EXEC_PATH}.bak")
    shutil.copy2(src=NOCD_PATCH, dst=SIMS_EXEC_PATH)

    # Add game to Bottle shortcuts
    add_program(name=SIMS_GAME_NAME, bottle_id=SIMS_BOTTLE_ID, path=SIMS_EXEC_PATH)

    # Create game .desktop file
    create_desktop_file(name=SIMS_GAME_NAME, bottle_id=SIMS_BOTTLE_ID, icon_path=SIMS_ICON_PATH)


if __name__ == "__main__":
    main()
