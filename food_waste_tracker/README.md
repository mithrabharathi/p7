# Food Waste & Surplus Redistribution Tracker

A Python file-handling application (Program 7) built with Streamlit.

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open in your browser. Use the tabs to add, view, search,
update, delete, and back up donation records.

## Project structure

| File | Purpose |
|---|---|
| `models.py` | OOP classes: `Donor`, `FoodItem`, `DonationRecord` (serialization) |
| `validators.py` | Regex-based validation for every input field |
| `file_manager.py` | All file I/O: create, read, append, search, update, delete, backup |
| `app.py` | Streamlit GUI, wires the above modules together |
| `data/donations.txt` | Text data file, one `\|`-delimited record per line |
| `data/backups/` | Timestamped backup copies |

## Description (100-150 words)

This application manages surplus-food donation records for a **Food
Waste & Surplus Redistribution Tracker**. Each record stores seven
fields: Donation ID, Donor Name, Food Item, Quantity (kg), Expiry
Date, Contact, and Status, saved as `|`-delimited lines in a plain
text file (`data/donations.txt`). File handling is implemented
through dedicated functions in `file_manager.py`, which together
demonstrate the `w`, `r`, `a`, `r+`, and `w+` opening modes and the
`read()`, `readline()`, `readlines()`, `write()`, `writelines()`,
`seek()`, and `tell()` methods, with every file closed automatically
via Python's `with` context manager. Input validation uses regular
expressions in `validators.py` to check the Donation ID format,
name/food-item text, numeric quantity, `dd-mm-yyyy` dates, and
phone/email contacts. The Streamlit GUI in `app.py` provides forms
and tables for data entry, search, update, and display, with
try/except exception handling and clear success/error messages
throughout.
