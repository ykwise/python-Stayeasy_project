from datetime import date
from models.room import DeluxeRoom
from pricing.pricing import calculate_nightly_charges
from pricing.pricing import calculate_nightly_charges, calculate_discounts,allocate_discounts,calculate_gst

room = DeluxeRoom()

charges = calculate_nightly_charges(
    date(2026, 11, 5),
    date(2026, 11, 12),
    room,
    3
)

for charge in charges:
    print(charge)

discounts = calculate_discounts(charges,3)
print(discounts)

charges = allocate_discounts(charges,discounts)
charges = calculate_gst(charges)

for night in charges:
    print(night)