"""
file_manager.py
----------------
All text-file I/O for the Food Waste & Surplus Redistribution Tracker
lives here, as separate user-defined functions, each documented with
the file-opening mode and file-handling methods it demonstrates.

Data file format: one DonationRecord per line, '|' delimited
(see models.py for the exact field order).

File opening modes demonstrated across this module: w, r, a, r+, w+
File handling methods demonstrated: read(), readline(), readlines(),
write(), writelines(), seek(), tell(), close()  (the last one is
implicit/explicit via the 'with' context manager, which always closes
the file even if an exception occurs).
"""

import os
import shutil
from datetime import datetime

from models import DonationRecord

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "donations.txt")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "data", "backups")


# --------------------------------------------------------------------------
# 1. CREATE FILE
# --------------------------------------------------------------------------
def create_file():
    """
    Create a brand-new (empty) data file, overwriting any existing one.

    Mode demonstrated : 'w'  (write - creates the file / truncates it)
    Methods demonstrated: close() via context manager
    """
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            pass  # an empty file is created; header not stored to keep parsing simple
        return True, f"New data file created at '{DATA_FILE}'."
    except Exception as e:
        return False, f"Could not create file: {e}"


def ensure_file_exists():
    """Utility: make sure the data file exists before any read/append/update."""
    if not os.path.exists(DATA_FILE):
        create_file()


# --------------------------------------------------------------------------
# 2. READ ALL RECORDS
# --------------------------------------------------------------------------
def read_all_records():
    """
    Read and return every record in the data file.

    Mode demonstrated : 'r'  (read only)
    Methods demonstrated: readlines(), tell()
    """
    ensure_file_exists()
    records = []
    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()          # readlines() -> list of lines
            _cursor_position = f.tell()    # tell() -> current stream position
        for line in lines:
            line = line.strip()
            if line:
                try:
                    records.append(DonationRecord.from_line(line))
                except ValueError:
                    continue  # skip corrupt lines rather than crash the app
        return True, records
    except FileNotFoundError:
        return False, "Data file not found."
    except Exception as e:
        return False, f"Error reading records: {e}"


# --------------------------------------------------------------------------
# 3. APPEND A NEW RECORD
# --------------------------------------------------------------------------
def append_record(record: DonationRecord):
    """
    Append one new donation record to the end of the data file.

    Mode demonstrated : 'a'  (append - never overwrites existing data)
    Methods demonstrated: write()
    """
    ensure_file_exists()
    try:
        # reject duplicate donation IDs
        ok, existing = read_all_records()
        if ok and any(r.donation_id == record.donation_id for r in existing):
            return False, f"Donation ID '{record.donation_id}' already exists."

        with open(DATA_FILE, "a") as f:
            f.write(record.to_line())      # write() -> writes a single string
        return True, f"Record '{record.donation_id}' added successfully."
    except Exception as e:
        return False, f"Error appending record: {e}"


# --------------------------------------------------------------------------
# 4. SEARCH FOR A RECORD
# --------------------------------------------------------------------------
def search_record(donation_id: str):
    """
    Search for a single record by donation_id (the key field).

    Mode demonstrated : 'r'
    Methods demonstrated: readline() (line-by-line scan)
    """
    ensure_file_exists()
    donation_id = donation_id.strip()
    try:
        with open(DATA_FILE, "r") as f:
            while True:
                line = f.readline()        # readline() -> one line at a time
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    record = DonationRecord.from_line(line)
                except ValueError:
                    continue
                if record.donation_id == donation_id:
                    return True, record
        return False, f"No record found with donation ID '{donation_id}'."
    except Exception as e:
        return False, f"Error searching record: {e}"


# --------------------------------------------------------------------------
# 5. UPDATE AN EXISTING RECORD
# --------------------------------------------------------------------------
def update_record(donation_id: str, updated_record: DonationRecord):
    """
    Update an existing record identified by donation_id.

    Mode demonstrated : 'r+'  (read + write, no truncation on open)
    Methods demonstrated: read(), seek(), write()

    Approach: read the whole file into memory, rebuild the content with
    the matching line replaced, then rewind with seek(0), write the new
    content, and truncate() off any leftover trailing bytes from the
    old (possibly longer) file content.
    """
    ensure_file_exists()
    donation_id = donation_id.strip()
    try:
        found = False
        with open(DATA_FILE, "r+") as f:
            content = f.read()             # read() -> whole file as one string
            lines = [ln for ln in content.split("\n") if ln.strip()]
            new_lines = []
            for ln in lines:
                try:
                    record = DonationRecord.from_line(ln)
                except ValueError:
                    new_lines.append(ln)
                    continue
                if record.donation_id == donation_id:
                    new_lines.append(updated_record.to_line().strip())
                    found = True
                else:
                    new_lines.append(ln)

            if not found:
                return False, f"No record found with donation ID '{donation_id}'."

            f.seek(0)                      # seek(0) -> rewind to start of file
            f.write("\n".join(new_lines) + "\n")
            f.truncate()                   # remove any leftover old bytes
        return True, f"Record '{donation_id}' updated successfully."
    except Exception as e:
        return False, f"Error updating record: {e}"


# --------------------------------------------------------------------------
# 6. DELETE A RECORD
# --------------------------------------------------------------------------
def delete_record(donation_id: str):
    """
    Delete a record identified by donation_id.

    Mode demonstrated : 'w+'  (write + read, truncates the file on open)
    Methods demonstrated: writelines()

    Approach: read existing records first (using read_all_records, a
    separate 'r' mode call), filter out the target, then reopen in
    'w+' mode to rewrite the remaining records.
    """
    donation_id = donation_id.strip()
    ok, records = read_all_records()
    if not ok:
        return False, records  # records holds the error message here

    remaining = [r for r in records if r.donation_id != donation_id]
    if len(remaining) == len(records):
        return False, f"No record found with donation ID '{donation_id}'."

    try:
        with open(DATA_FILE, "w+") as f:
            f.writelines([r.to_line() for r in remaining])  # writelines() -> list of strings
        return True, f"Record '{donation_id}' deleted successfully."
    except Exception as e:
        return False, f"Error deleting record: {e}"


# --------------------------------------------------------------------------
# 7. BACKUP THE DATA FILE
# --------------------------------------------------------------------------
def backup_file():
    """
    Create a timestamped backup copy of the current data file.

    Mode demonstrated : 'r' (source) and 'w' (destination)
    Methods demonstrated: read(), write()
    """
    ensure_file_exists()
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"donations_backup_{timestamp}.txt")

        with open(DATA_FILE, "r") as src:
            data = src.read()              # read() -> entire file content
        with open(backup_path, "w") as dst:
            dst.write(data)                # write() -> dump content to backup file

        return True, f"Backup created at '{backup_path}'."
    except Exception as e:
        return False, f"Error creating backup: {e}"


def list_backups():
    """Return list of available backup file names (helper for the UI)."""
    if not os.path.isdir(BACKUP_DIR):
        return []
    return sorted(os.listdir(BACKUP_DIR), reverse=True)
