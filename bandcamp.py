"""
Processes bandcamp zip files and copies the contained files into their correct
directory on NAS.
"""
from pathlib import Path
import re
import shutil
from zipfile import ZipFile

import click

nas_root = Path('/net/nas/volume1/music')
file_type_mapping = {'m4a': nas_root / 'aac',
                     'flac': nas_root / 'flac'}


def move_file(root_dir, archive_file, compressed_file, match):
    plain_file = Path(archive_file.extract(compressed_file))
    destination_dir = root_dir / match.group(1) / match.group(2)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_file = destination_dir / f"{match.group(3)}-{match.group(4)}"
    shutil.copyfile(plain_file, destination_file)
    plain_file.unlink()


@click.command()
@click.argument('file')
def process(file):
    """
    Main function which will be called from the command line.
    file: passed in from cmd line.
    """
    filename_regex = re.compile("(.*) - (.*) - ([0-9]*) (.*)")
    with ZipFile(file) as archive_file:
        for compressed_file in archive_file.namelist():
            try:
                match = filename_regex.match(compressed_file)
                for file_type in file_type_mapping:
                    if file_type in compressed_file:
                        move_file(file_type_mapping[file_type],
                                  archive_file,
                                  compressed_file,
                                  match)
            except Exception as e:
                print(f"Failed regex on {compressed_file}: {e}")


if __name__ == "__main__":
    process()
