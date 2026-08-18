"""
models.py
---------
OOP classes for the Food Waste & Surplus Redistribution Tracker.

Classes
-------
Donor          : holds donor/household identity and contact info.
FoodItem       : holds details about the surplus food being donated.
DonationRecord : composition of Donor + FoodItem + record-level fields
                 (donation id, status). Knows how to serialize itself
                 to/from a single line of the text data file.

The record is stored in the text file as a single '|' delimited line:

    donation_id|donor_name|food_item|quantity_kg|expiry_date|contact|status

That gives 7 fields in total (comfortably more than the required minimum
of six).
"""

from dataclasses import dataclass

FIELD_SEPARATOR = "|"
FIELDS = [
    "donation_id",
    "donor_name",
    "food_item",
    "quantity_kg",
    "expiry_date",
    "contact",
    "status",
]


@dataclass
class Donor:
    """Represents the person/organisation donating surplus food."""
    name: str
    contact: str  # phone number or email


@dataclass
class FoodItem:
    """Represents the surplus food item being donated."""
    item_name: str
    quantity_kg: str
    expiry_date: str  # dd-mm-yyyy


class DonationRecord:
    """
    Composition of Donor + FoodItem plus record-level bookkeeping fields.
    Provides serialization helpers used by file_manager.py.
    """

    def __init__(self, donation_id, donor: Donor, food: FoodItem, status="Pending"):
        self.donation_id = donation_id
        self.donor = donor
        self.food = food
        self.status = status

    # ---------- serialization helpers ----------

    def to_line(self) -> str:
        """Convert this record into a single '|' delimited text line."""
        values = [
            self.donation_id,
            self.donor.name,
            self.food.item_name,
            str(self.food.quantity_kg),
            self.food.expiry_date,
            self.donor.contact,
            self.status,
        ]
        return FIELD_SEPARATOR.join(values) + "\n"

    @staticmethod
    def from_line(line: str) -> "DonationRecord":
        """Reconstruct a DonationRecord object from a text file line."""
        parts = line.strip("\n").split(FIELD_SEPARATOR)
        if len(parts) != len(FIELDS):
            raise ValueError(f"Corrupt record line: {line!r}")
        donation_id, donor_name, item_name, qty, expiry, contact, status = parts
        donor = Donor(name=donor_name, contact=contact)
        food = FoodItem(item_name=item_name, quantity_kg=qty, expiry_date=expiry)
        return DonationRecord(donation_id, donor, food, status)

    def to_dict(self) -> dict:
        return {
            "Donation ID": self.donation_id,
            "Donor Name": self.donor.name,
            "Food Item": self.food.item_name,
            "Quantity (kg)": self.food.quantity_kg,
            "Expiry Date": self.food.expiry_date,
            "Contact": self.donor.contact,
            "Status": self.status,
        }
