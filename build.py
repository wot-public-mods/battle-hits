# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

"""
Build script for creating and packaging World of Tanks modifications.

This script handles:
- Compiling Python scripts.
- Publishing Adobe Animate projects.
- Packaging mod files into a .wotmod archive.
- Creating a distributable .zip archive.
- Copying the mod to the game directory and running the game.
"""

import argparse
import datetime
import json
import logging
import os
import pathlib
import random
import shutil
import string
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, Dict, List, Optional, Set

try:
    import psutil
except ImportError:
    raise ImportError("psutil is not installed. Please run 'pip install psutil' to install it.")


# --- Logger Setup ---

class ElapsedFormatter(logging.Formatter):
    """A logging formatter that includes the elapsed time since initialization."""

    def __init__(self) -> None:
        """Initializes the formatter and records the start time."""
        super().__init__()
        self.start_time = time.time()

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record to include elapsed time."""
        elapsed_seconds = record.created - self.start_time
        elapsed = datetime.timedelta(seconds=elapsed_seconds)
        # Format as S.MS for quick reading
        return f"{elapsed.seconds:03d}.{int(elapsed.microseconds / 1000):03d} {record.getMessage()}"


def setup_logger() -> logging.Logger:
    """Configures and returns a root logger."""
    handler = logging.StreamHandler()
    handler.setFormatter(ElapsedFormatter())

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


# --- Configuration Classes ---

class AppConfig:
    """A class to hold the application configuration from build.json."""

    class Software:
        """Holds paths to external software."""
        def __init__(self, data: Dict[str, Any]) -> None:
            self.animate: Optional[str] = data.get('animate')
            self.python: Optional[str] = data.get('python')

    class Game:
        """Holds game-related configuration."""
        def __init__(self, data: Dict[str, Any]) -> None:
            self.force: bool = data.get('force', False)
            self.folder: Optional[str] = data.get('folder')
            self.version: Optional[str] = data.get('version')

    class Info:
        """Holds mod metadata."""
        def __init__(self, data: Dict[str, Any]) -> None:
            self.id: Optional[str] = data.get('id')
            self.name: Optional[str] = data.get('name')
            self.description: Optional[str] = data.get('description')
            self.version: Optional[str] = data.get('version')

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initializes the main configuration object from a dictionary."""
        self.version: int = data.get('version', 0)
        self.software = self.Software(data.get('software', {}))
        self.game = self.Game(data.get('game', {}))
        self.info = self.Info(data.get('info', {}))


# --- Utility Functions ---

def rand_str(num: int) -> str:
    """Generates a random alphanumeric string of a given length."""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(num))


def copytree(source: str, destination: str, ignore: Optional[callable] = None) -> None:
    """
    A custom copytree implementation that is more lenient about existing directories.
    
    Args:
        source: The source directory path.
        destination: The destination directory path.
        ignore: A callable compatible with shutil.ignore_patterns.
    """
    source_path = pathlib.Path(source)
    dest_path = pathlib.Path(destination)
    dest_path.mkdir(parents=True, exist_ok=True)

    names = os.listdir(source_path)
    ignored_names: Set[str] = ignore(str(source_path), names) if ignore else set()

    for name in names:
        if name in ignored_names or '.gitkeep' in name:
            continue

        srcname = source_path / name
        dstname = dest_path / name

        try:
            if srcname.is_dir():
                copytree(str(srcname), str(dstname), ignore)
            else:
                shutil.copy2(str(srcname), str(dstname))
        except (IOError, os.error) as why:
            logger.error("Can't copy %s to %s: %s", srcname, dstname, str(why))


def zip_folder(source: str, destination: str, mode: str = 'w', compression: int = zipfile.ZIP_STORED) -> None:
    """
    Zips a folder, including empty directories, with consistent metadata.

    Args:
        source: The source directory to zip.
        destination: The path to the output zip file.
        mode: The file mode for the zip file ('w', 'a', etc.).
        compression: The compression method to use.
    """
    source_path = pathlib.Path(source)
    with zipfile.ZipFile(destination, mode, compression) as zipfh:
        # Use a fixed timestamp for reproducible builds
        now = tuple(datetime.datetime.now().timetuple())[:6]
        for file_path in source_path.rglob('*'):
            arcname = file_path.relative_to(source_path)
            if file_path.is_dir():
                # Add directory entry
                info = zipfile.ZipInfo(str(arcname).replace('\\', '/') + '/', now)
                info.compress_type = compression
                zipfh.writestr(info, '')
            else:
                # Add file entry with standard permissions
                info = zipfile.ZipInfo(str(arcname).replace('\\', '/'), now)
                info.external_attr = 33206 << 16 # -rw-rw-rw-
                info.compress_type = compression
                zipfh.writestr(info, file_path.read_bytes())


def is_process_running(path: str) -> bool:
    """
    Checks if a process with the given executable name is running.

    Args:
        path: The path to the executable.

    Returns:
        True if the process is running, False otherwise.
    """
    process_name = pathlib.Path(path).name.lower()
    return any(proc.info['name'].lower() == process_name for proc in psutil.process_iter(['name']))


# --- Build Steps ---

def build_flash(config: AppConfig, args: argparse.Namespace) -> None:
    """
    Builds Adobe Animate projects (.fla, .xfl).

    Args:
        config: The application configuration.
        args: The command-line arguments.
    """
    if not args.flash:
        return

    files_to_process = list(pathlib.Path('as3').rglob('*.fla')) + list(pathlib.Path('as3').rglob('*.xfl'))
    if not files_to_process:
        logger.info("No Flash files found to build.")
        return

    if not config.software.animate or not is_process_running(config.software.animate):
        raise Exception('Adobe Animate is not running or not configured in build.json.')

    for file_path in files_to_process:
        log_path = file_path.with_suffix('.log')
        jsfl_file = pathlib.Path(f'build-{rand_str(5)}.jsfl')
        document_uri = file_path.resolve().as_uri()
        log_file_uri = log_path.resolve().as_uri()

        # JSFL commands to publish the document and save compiler errors
        jsfl_content = f'fl.publishDocument("{document_uri}", "Default");\n'
        jsfl_content += f'fl.compilerErrors.save("{log_file_uri}", false, true);\n'
        jsfl_file.write_text(jsfl_content, encoding='utf-8')

        try:
            subprocess.check_call(
                [config.software.animate, '-e', str(jsfl_file), '-AlwaysRunJSFL'],
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError:
            logger.exception('build_flash failed for %s', file_path)

        # Cleanup: Poll until the file is no longer locked by Animate
        while jsfl_file.exists():
            try:
                jsfl_file.unlink()
            except OSError:
                time.sleep(0.01)

        # Check for compilation errors
        log_data = ''
        if log_path.is_file():
            lines = log_path.read_text(encoding='utf-8', errors='ignore').splitlines()
            if len(lines) > 1:
                log_data = '\n'.join(lines[:-2])  # Animate adds extra lines at the end
            log_path.unlink()

        if log_data:
            logger.error('Failed flash publish %s\n%s', file_path, log_data)
        else:
            logger.info('Flash published: %s', file_path)


def build_python(config: AppConfig) -> None:
    """
    Compiles all .py files into .pyc bytecode.

    Args:
        config: The application configuration.
    """
    python_source_dir = pathlib.Path('python')
    if not config.software.python:
        raise ValueError("Python executable path is not configured in build.json")

    for file_path in python_source_dir.rglob('*.py'):
        try:
            subprocess.check_output(
                [config.software.python, '-m', 'py_compile', str(file_path)],
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8'
            )
            logger.info('Python compiled: %s', file_path)
        except subprocess.CalledProcessError as e:
            logger.error('Python fail compile: %s\n%s', file_path, e.output)


def main() -> None:
    """The main entry point for the build script."""
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description='Build script for WoT mods.')
    parser.add_argument('--flash', action='store_true', help='Build flash assets.')
    parser.add_argument('--ingame', action='store_true', help='Copy the build into the game directory.')
    parser.add_argument('--distribute', action='store_true', help='Create a distributable archive.')
    parser.add_argument('--run', action='store_true', help='Run the game after a successful build.')
    args = parser.parse_args()

    # --- Configuration Loading ---
    config_path = pathlib.Path('build.json')
    if not config_path.is_file():
        raise FileNotFoundError('Config not found: build.json')

    with config_path.open('r', encoding='utf-8') as fh:
        config_data = json.load(fh)
        config = AppConfig(config_data)

    # Determine game folder and version from config or environment variables
    if config.game.force:
        game_folder = pathlib.Path(config.game.folder) if config.game.folder else None
        game_version = config.game.version
    else:
        game_folder = pathlib.Path(os.environ.get('WOT_FOLDER', config.game.folder or ''))
        game_version = os.environ.get('WOT_VERSION', config.game.version or '')

    if not game_folder or not game_version:
        raise ValueError("Game folder or version is not configured.")

    # --- Folder Preparation ---
    temp_dir = pathlib.Path('temp')
    build_dir = pathlib.Path('build')
    if temp_dir.is_dir():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    if build_dir.is_dir():
        shutil.rmtree(build_dir)
    build_dir.mkdir()

    # --- Build Steps ---
    logger.info("Starting build process...")
    build_python(config)
    build_flash(config, args)

    # --- Packaging ---
    logger.info("Packaging mod...")
    package_name = f'{config.info.id}_{config.info.version}.wotmod'

    # Generate meta.xml using ElementTree for safe XML creation
    root = ET.Element('root')
    ET.SubElement(root, 'id').text = config.info.id
    ET.SubElement(root, 'version').text = config.info.version
    ET.SubElement(root, 'name').text = config.info.name
    ET.SubElement(root, 'description').text = config.info.description
    
    # Pretty print the XML
    ET.indent(root, space="    ")
    meta_content = ET.tostring(root, encoding='unicode')

    # Copy resources to temp directory
    if pathlib.Path('resources/in').is_dir():
        copytree('resources/in', str(temp_dir / 'res'))
    if pathlib.Path('as3/bin').is_dir():
        copytree('as3/bin', str(temp_dir / 'res/gui/flash'))
    copytree('python', str(temp_dir / 'res/scripts/client'), ignore=shutil.ignore_patterns('*.py'))
    (temp_dir / 'meta.xml').write_text(meta_content, encoding='utf-8')

    # Create the .wotmod package
    zip_folder(str(temp_dir), str(build_dir / package_name))
    logger.info("Package created: %s", build_dir / package_name)

    # --- Post-Build Actions ---
    wot_packages_dir = game_folder / 'mods' / game_version
    if args.ingame:
        if not wot_packages_dir.is_dir():
            raise FileNotFoundError(f'WoT mods folder not found: {wot_packages_dir}')

        # Terminate game client if running
        exe_name = 'worldoftanks.exe'
        for proc in psutil.process_iter(['name', 'pid']):
            if exe_name in proc.info['name'].lower():
                try:
                    p = psutil.Process(proc.info['pid'])
                    p.terminate()
                    logger.info('WoT client closing (pid: %s)', proc.info['pid'])
                    p.wait(timeout=10)
                except psutil.Error as e:
                    logger.warning("Could not terminate WoT client (pid: %s): %s", proc.info['pid'], e)

        logger.info('Copying package to: %s', wot_packages_dir / package_name)
        shutil.copy2(str(build_dir / package_name), str(wot_packages_dir))

    if args.distribute:
        logger.info("Creating distribution archive...")
        dist_dir = temp_dir / 'distribute'
        dist_mods_dir = dist_dir / 'mods' / game_version
        dist_mods_dir.mkdir(parents=True)

        shutil.copy2(str(build_dir / package_name), str(dist_mods_dir))
        if pathlib.Path('resources/out').is_dir():
            copytree('resources/out', str(dist_dir))

        zip_name = f'{config.info.id}_{config.info.version}.zip'
        zip_folder(str(dist_dir), str(build_dir / zip_name))
        logger.info("Distribution archive created: %s", build_dir / zip_name)

    # --- Cleanup ---
    logger.info("Cleaning up temporary files...")
    cleanup_paths: List[pathlib.Path] = [
        temp_dir,
        pathlib.Path('EvalScript error.tmp'),
        pathlib.Path('as3/DataStore')
    ]
    cleanup_paths.extend(pathlib.Path('python').rglob('*.pyc'))

    for path in cleanup_paths:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.is_file():
            path.unlink(missing_ok=True)

    if args.run:
        executable_path = game_folder / 'worldoftanks.exe'
        if executable_path.is_file():
            logger.info("Starting World of Tanks client...")
            subprocess.Popen([str(executable_path)])
        else:
            logger.warning("Could not find game executable to run at: %s", executable_path)

    logger.info("Build finished successfully.")


if __name__ == '__main__':
    logger = setup_logger()
    try:
        main()
    except Exception as e:
        logger.exception("An unhandled error occurred: %s", e)
        sys.exit(1)
