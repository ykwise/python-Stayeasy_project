import sqlite3
def create_tables():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    #Rooms Table
    cursor.execute('''
                Create Table If Not Exists Rooms(
                Room_id int Primary Key Not Null,
                Room_Type Text Not Null Check(Room_Type in ('STANDARD','DELUXE','SUITE')),
                Floor int Not null                
                )
            ''')

    print("Rooms Table Created Succesfully")

    #Guests Table
    cursor.execute('''
                Create Table If not Exists Guests(
                Guest_Name Text Not Null,
                Phone_Number Text Primary Key check(
                    length(Phone_Number) = 10 and 
                    (Phone_Number like '6%' or
                     Phone_Number like '7%' or
                     Phone_Number like '8%' or
                     Phone_Number like '9%' )
                ),

                Email Text check(Email like '%@gmail.com') Not Null
                
                )

                ''')
    print("Guests Table Created Successfully")

    #Bookings Table
    cursor.execute('''
                Create Table If Not Exists Bookings(
                Booking_Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Guest_Name Text Not Null,
                Phone_Number Text check(
                                    length(Phone_Number) = 10 and 
                                    (Phone_Number like '6%' or
                                     Phone_Number like '7%' or
                                     Phone_Number like '8%' or
                                     Phone_Number like '9%' )
                                    ),
                Email Text check(Email like '%@gmail.com') Not Null,
                No_of_Guests int check(No_of_Guests > 0),
                Check_In Text Not Null,
                Check_Out Text Not Null,
                Room_id int Not Null,
                Status Text Check(Status in ('CONFIRMED','CHECKED_IN','CHECKED_OUT','CANCELLED')),
                Foreign Key(Room_id) references Rooms(Room_id),
                Foreign Key(Phone_Number) references Guests(Phone_Number)
                )

                    ''')
    print("Bookings Table Created Successfully")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Booking_Nightly_Charges (
            Charge_Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Booking_Id INTEGER NOT NULL,
            Stay_Date TEXT NOT NULL,
            Day_Name TEXT NOT NULL,
            Room_Tariff REAL NOT NULL,
            Extra_Guest_Charge REAL NOT NULL,
            GST_Rate REAL NOT NULL,
            GST_Amount REAL NOT NULL,
            Night_Total REAL NOT NULL,
            Discount Decimal Not Null Default 0,
            Discounted_Amount Decimal Not Null Default 0,
            Total_Rate Decimal Not Null Default 0,
            FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id),
            UNIQUE (Booking_Id, Stay_Date)
        )
    """)
    print("Booking_Nightly Charges Table Created Successfully")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Booking_Billing_Summary (
        Booking_Id INTEGER PRIMARY KEY,
        Total_Charges REAL NOT NULL,
        Long_Stay_Discount REAL NOT NULL,
        Loyalty_Discount REAL NOT NULL,
        Total_Discount REAL NOT NULL,
        Taxable_Amount REAL NOT NULL,
        Total_GST REAL NOT NULL,
        Final_Amount REAL NOT NULL,
        FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id)
    )
""")
    print("Booking_Billing_Summary_Generated")

    conn.commit()
    conn.close()

#Showing Table data
def show_table(tablename):
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    que = f"select * from {tablename}"
    cursor.execute(que)
    data = cursor.fetchall()
    print(f"Table: {tablename}")
    for row in data:
        print(row)
    print()