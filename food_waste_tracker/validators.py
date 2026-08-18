"""
validators.py
--------------
Regular-expression based input validation for the Food Waste &
Surplus Redistribution Tracker.

Each function returns a tuple: (is_valid: bool, message: str)
so the GUI layer can display a meaningful success/error message.
"""

import re
from datetime import datetime

# Donation ID like D001, D023, D999
DONATION_ID_PATTERN = re.compile(r"^D\d{3,5}$")

# Donor / household name - letters, spaces, apostrophes, hyphens
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s'\-]{1,49}$")

# Food item name - letters, digits, spaces, common punctuation
FOOD_ITEM_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\s\-\&\(\)]{1,49}$")

# Quantity in kg - positive number, up to 2 decimal places
QUANTITY_PATTERN = re.compile(r"^\d+(\.\d{1,2})?$")

# Date in dd-mm-yyyy format
DATE_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}$")

# Indian-style 10 digit phone number OR a basic email address
PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")
EMAIL_PATTERN = re.compile(r"^[\w\.\-]+@[\w\-]+\.[a-zA-Z]{2,}$")


def validate_donation_id(value: str):
    if DONATION_ID_PATTERN.match(value.strip()):
        return True, "Valid donation ID."
    return False, "Donation ID must look like 'D001' (D followed by 3-5 digits)."


def validate_name(value: str):
    if NAME_PATTERN.match(value.strip()):
        return True, "Valid name."
    return False, "Name must be 2-50 letters (spaces, hyphens, apostrophes allowed)."


def validate_food_item(value: str):
    if FOOD_ITEM_PATTERN.match(value.strip()):
        return True, "Valid food item."
    return False, "Food item must be 2-50 alphanumeric characters."


def validate_quantity(value: str):
    if QUANTITY_PATTERN.match(value.strip()):
        return True, "Valid quantity."
    return False, "Quantity must be a positive number, e.g. 5 or 5.5 (kg)."


def validate_date(value: str):
    value = value.strip()
    if not DATE_PATTERN.match(value):
        return False, "Date must be in dd-mm-yyyy format, e.g. 25-12-2026."
    try:
        datetime.strptime(value, "%d-%m-%Y")
    except ValueError:
        return False, "That date does not exist. Check day/month values."
    return True, "Valid date."


def validate_contact(value: str):
    value = value.strip()
    if PHONE_PATTERN.match(value) or EMAIL_PATTERN.match(value):
        return True, "Valid contact."
    return False, "Contact must be a 10-digit phone number or a valid email address."


def validate_record(donation_id, donor_name, food_item, quantity, expiry_date, contact):
    """
    Run all field validations together.
    Returns (True, "") if everything is valid,
    otherwise (False, "first error message encountered").
    """
    checks = [
        validate_donation_id(donation_id),
        validate_name(donor_name),
        validate_food_item(food_item),
        validate_quantity(quantity),
        validate_date(expiry_date),
        validate_contact(contact),
    ]
    for is_valid, message in checks:
        if not is_valid:
            return False, message
    return True, "All fields valid."
