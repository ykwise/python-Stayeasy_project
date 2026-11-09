# StayEasy – Hotel Reservation and Billing System

## About the Project

StayEasy is a Python-based hotel reservation and billing system developed to manage the day-to-day activities of a hotel. It allows users to check room availability, make bookings, manage guest check-in and check-out, cancel reservations, and generate invoices.

The application uses SQLite to store guest and booking information, so the data remains available even after closing the program.

## Features

- Search for available rooms based on room type, number of guests, and dates.
- Create and manage hotel reservations.
- Handle guest check-in and check-out.
- Cancel bookings and calculate refunds based on cancellation rules.
- Generate invoices with a detailed breakdown of charges.
- View booking details and guest stay history.
- Generate occupancy and revenue reports.
- Export booking details to a CSV file.
- Load room information from a CSV file.

## Technologies Used

- Python 3
- SQLite
- CSV File Handling
- Object-Oriented Programming

## Project Structure

```text
StayEasy/
│
├── database/
├── models/
├── Exceptions/
├── pricing/
├── invoices/
│
├── rooms.csv
├── program.py
├── invoice.py
├── requirements.txt
└── README.md
```

## Installation and Setup

**1. Clone the repository**

```bash
git clone <repository-url>
```

**2. Navigate to the project directory**

```bash
cd StayEasy
```

**3. Create a virtual environment**

```bash
python -m venv .venv
```

**4. Activate the virtual environment**

Windows:

```bash
.venv\Scripts\activate
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Run the application**

```bash
python program.py
```

