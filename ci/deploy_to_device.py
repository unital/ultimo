# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

from pathlib import Path
import subprocess

import click


@click.command()
def deploy():
    """Deploy files to a device via mpremote"""
    try:
        deploy_py_files(Path("docs/source/examples"), ":")
        deploy_py_files(Path("docs/source/examples/devices"), ":/devices")
        deploy_py_files(Path("src/ultimo"), ":/lib/ultimo")
        deploy_py_files(Path("src/ultimo_machine"), ":/lib/ultimo_machine")
        deploy_py_files(Path("src/ultimo_display"), ":/lib/ultimo_display")
    except subprocess.CalledProcessError as exc:
        print("Error:")
        print(exc.stderr)
        raise

def deploy_py_files(path: Path, destination):
    try:
        mpremote("mkdir", destination)
    except subprocess.CalledProcessError as exc:
        # path exists, clear out old files
        print('remove', listdir(destination))
        for file in listdir(destination):
            file = file.decode('utf-8')
            if not file.endswith('.py'):
                continue
            try:
                mpremote("rm", f"{destination}/{file}")
            except subprocess.CalledProcessError as exc:
                # probably a directory
                pass

    for file in path.glob("*.py"):
        mpremote("cp", str(file), f"{destination}/{file.name}")


def listdir(directory):
    listing = mpremote("ls", directory)
    if listing is not None:
        listing = listing.splitlines(1)[1]
        return listing.split()[1::2]
    else:
        return []


def mpremote(command, *args):
    result = subprocess.run(["mpremote", command, *args], capture_output=True, check=True)
    return result.stdout

if __name__ == "__main__":
    deploy()