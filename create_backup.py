#!/usr/bin/env python3

import os
import tarfile
from datetime import datetime

def create_backup():
    """Creates a backup of the repository as a .tar.gz file."""

    # Get the current date and time for the filename
    now = datetime.now()
    datetimestr = now.strftime("%Y%m%d-%H%M%S")
    backup_filename = f"bookfix-backup-{datetimestr}.tar.gz"
    backup_path = os.path.join("/home/danno/MyApps/BookFix/backup", backup_filename)

    # Exclude directories
    exclude_dirs = ["./venv", "./models", "./backup" "/.git"]

    # Create the backup
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            for item in os.listdir("."):
                if item not in [d.lstrip("./") for d in exclude_dirs]:
                    tar.add(item)
        print(f"Successfully created backup: {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")

if __name__ == "__main__":
    create_backup()
