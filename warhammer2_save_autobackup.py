#!/usr/bin/env python

"""
Script to backup TW WH2 saves while running.
Outdir, checking interval and number of backups per save can
be adjusted with command line arguments.
expected usage
python warhammer2_save_autobackup.py --outdir {{OUTDIR}} --interval {{NUM}} --num_saves {{NUM}}
"""

import os
import argparse
import glob
import shutil
import datetime
import schedule
import time


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Run to automatically back up warhammer 2 saves."
            " Defaults to check every 20 minutes."
        )
    )
    parser.add_argument(
        "--interval", default=20, help="Number of minutes to backup saves"
    )
    parser.add_argument(
        "--num_saves", default=5, help="Number of saves to keep at one time"
    )
    parser.add_argument(
        "--outdir", default="wh2_backup", help="Directory to put backup saves"
    )

    num_interval = parser.parse_args().interval
    num_saves = parser.parse_args().num_saves
    outdir = parser.parse_args().outdir

    print("Initialising and creating initial save copies")

    os.makedirs(outdir, exist_ok=True)
    appdata = os.path.expandvars("%appdata%")
    save_folder = os.path.join(
        appdata, "The Creative Assembly", "Warhammer2", "save_games"
    )
    save_files = glob.glob(f"{save_folder}/*.save")
    for file in save_files:
        back_up_saves(file, outdir, num_saves)

    print("Successfully initialised.")
    print(f"Ongoing backup checks occuring every {num_interval} minutes")

    for file in save_files:
        schedule.every(num_interval).minutes.do(
            back_up_saves, file, outdir, num_saves
        )

    while True:
        schedule.run_pending()
        time.sleep(1)


def back_up_saves(file, outdir, num_saves):
    myfile = WH2SaveFile(file)
    check_existing_copy = glob.glob(
        f"{outdir}/{myfile.save_name}.{myfile.save_start}*"
    )
    outname = (
        f"{myfile.save_name}.{myfile.save_start}.{myfile.date_modified}.save"
    )
    if not check_existing_copy:
        print(f"Making a backup for {os.path.basename(file)}")
        shutil.copyfile(file, os.path.join(outdir, outname))
    else:
        if len(check_existing_copy) > num_saves:
            check_existing_copy = sorted(check_existing_copy)
            check_existing_copy.remove(check_existing_copy[0])

        for backupfile in check_existing_copy:
            backup_date_modified = os.path.basename(backupfile).split(".")[2]
            print(
                f"Checking if {myfile.filename} has been modified since last check."
            )
            if myfile.date_modified != int(backup_date_modified):
                print(f"Making new backup for {myfile.filename}")
                shutil.copyfile(file, os.path.join(outdir, outname))
            else:
                print(f"{myfile.filename} is unmodified since backup.")


class WH2SaveFile:
    def __init__(self, fname):
        self.date_modified = int(os.path.getmtime(fname))
        self.filename = os.path.basename(fname)
        name_split_up = self.filename.split(".")
        self.save_name = name_split_up[0] + name_split_up[1]
        self.save_start = name_split_up[2]


if __name__ == "__main__":
    main()
