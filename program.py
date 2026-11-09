#------------------------------
import sqlite3
from datetime import datetime,date,timedelta
from abc import ABC,abstractmethod
from Exceptions.exceptions import RoomException,InvalidStatusException,BookingException,DateException
import csv
from models.guest import Guest as gt
from models.booking import Booking as bk
from models.room import RoomType,StandardRoom,DeluxeRoom,SuiteRoom
from database.tables import create_tables,show_table
from pricing.pricing import calculate_final_bill
from invoice import generate_invoice

#load rooms data
def load_rooms():
    conn = sqlite3.connect("stayeasy.db")       
    cursor = conn.cursor()
    logs = []
    rooms = set()
    rooms_type_obs = {}


    with open("rooms.csv","r") as file:
        content = csv.reader(file)

        next(content)        

        for row in content:
            room_id = row[0]
            room_type = row[1].strip().upper()
            floor = row[2]

            #print(f"Room No: {room_id} | Room Type :{room_type} | Floor : {floor}")

            try:
                room_id = int(row[0])
                
                if room_id in rooms:
                    raise RoomException(f"Room Id {room_id} already exists in Rooms Table")
                
                room_type = row[1].strip().upper()
                if room_type == "":
                    raise RoomException("Name Cannot be Empty")

                if room_type not in ["STANDARD","DELUXE","SUITE"]:
                    raise RoomException(f"Invalid Room Type {room_type}")

                #--------------------------                 
                floor = int(row[2])
                if floor == "":
                    raise RoomException("Floor is Empty")

                #---------------------
                

                rooms.add(room_id)

                #After Validating , Pushing the Values to Rooms Table
                query = "Insert into Rooms(Room_id,Room_Type,Floor) Values(?,?,?)"
                cursor.execute(query,(room_id,room_type,floor))
                #conn.commit()
                print(f"Data Inserted With Room No : {room_id}")
                print()

                #creating objects of specific RoomType and Keeping in dict
                if room_type == "STANDARD":
                    rooms_type_obs[room_id] = StandardRoom()
                elif room_type == "DELUXE":
                    rooms_type_obs[room_id] = DeluxeRoom()
                else:
                    rooms_type_obs[room_id] = SuiteRoom()



            except RoomException as e:
                logs.append(f"Rooms.csv | {room_id} | {e}")

            except ValueError as e:
                logs.append(f"Rooms.csv | {room_id} |{e}")

            except sqlite3.IntegrityError:
                print(f"Room Id : {room_id} Already Exists in Rooms Table")
    conn.commit()
    
    #--------------------
    #creating errorlog file
    with open("app.log","w") as errorfile:
        for errors in logs:
            errorfile.writelines(errors + "\n")

    print("Error Logs sent to app.log ")

    #----------------------------
    cursor.execute("Select Room_id,Room_Type from Rooms")
    data = cursor.fetchall()

    for row in data:
        rid = row[0]
        rtype = row[1]

        if rtype == "STANDARD":
            rooms_type_obs[rid] = StandardRoom()
        elif rtype == "DELUXE":
            rooms_type_obs[rid] = DeluxeRoom()
        else:
            rooms_type_obs[rid] = SuiteRoom()
    

    print()
    show_table("Rooms")
    print()
    for errors in logs:
        print(errors)
    print()

    #print("Room Type Objects")
    #print(rooms_type_dict)

    # for id in rooms_type_obs:
    #     tarrif = rooms_type_obs[id].get_tarrif()
    #     roomtype = rooms_type_obs[id].roomtype
    #     print(f"Room No: {id} | Room Type: {roomtype} | Tarrif: {tarrif}")

    conn.close()

    return rooms_type_obs


#Checking Available Rooms
def check_available_rooms(type,guests,checkin,checkout):
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()
    room_types = room_type_obs
    avialable_rooms = []

    req_checkin_fmt = datetime.strptime(checkin,"%d-%m-%Y")
    req_checkout_fmt = datetime.strptime(checkout,"%d-%m-%Y")

    query = "Select * from Rooms Where Room_Type = ?"
    cursor.execute(query,(type,))
    roomsdata = cursor.fetchall()
    for row in roomsdata:
        is_available = True
        rid = row[0]

        max_guests = room_types[rid].get_max_guests()

        if guests > max_guests:
            continue

        query = "Select Check_In,Check_Out from Bookings where Room_id = ? and Status in ('CONFIRMED','CHECKED_IN')"
        cursor.execute(query,(rid,))
        data = cursor.fetchall()
        for row in data:
            exist_checkin = datetime.strptime(row[0],"%d-%m-%Y")
            exist_checkout = datetime.strptime(row[1],"%d-%m-%Y")

            if req_checkin_fmt < exist_checkout and req_checkout_fmt > exist_checkin:
                is_available = False
                break

        if is_available:
            avialable_rooms.append(rid)

    print(f"Available Rooms:{avialable_rooms} ")

    return avialable_rooms

#see avialable rooms
def see_alternative_rooms(type,guests,checkin,checkout):
    alternate_rooms = {}

    roomtypes = ["STANDARD","DELUXE","SUITE"]
    for t in roomtypes:
        if t == type:
            continue
        avail_rooms = check_available_rooms(t,guests,checkin,checkout)

        if avail_rooms :
            alternate_rooms[t] = avail_rooms

    return alternate_rooms


#creating booking
def make_booking():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()


    print("-----Booking Details----")
    name = input("Enter Guest Name: ").strip().upper()

    while name == "":
        print("Name Cannot be Empty")
        name = input("Enter Guest Name: ").strip().upper()

    
    phone = input("Enter Phone Number: ").strip()
    while (len(phone) != 10) or not phone.isdigit():
        print("Phone Number does not have 10 digits")
        phone = input("Enter Phone Number: ").strip()
    while not( phone.startswith("6") or  phone.startswith("7")  or phone.startswith("8") or  phone.startswith("9") ):
        print("Phone Number does not start with 6 or 7 or 8 or 9")
        phone = input("Enter Phone Number: ").strip()
    
    email = input("Enter Email: ").strip().lower()
    while(not email.endswith("@gmail.com")):
        print("Please Enter Valid Email")
        email = input("Enter Email: ").strip().lower()
    
    guests = int(input("Enter No.of Guests: "))
    while guests < 1:
        print("guests should be more than 0")
        guests = int(input("Enter No.of Guests: "))
    
    roomtype = input("Enter Room Type(Standard/Deluxe/Suite): ").strip().upper()
    while roomtype not in ["STANDARD","DELUXE","SUITE"]:
        print("Please Enter Valid Room Type")
        roomtype = input("Enter Room Type(Standard/Deluxe/Suite): ").strip().upper()
    
        
    
    today = date.today()
    today_fmt = today.strftime("%d-%m-%Y")
    print(f"Today Date: {today_fmt}")
    
    #Validating Checkin and Checkout   
    while True:
        try:
            #Taking Checking input
            checkinday = int(input("Enter checkin-day(DD) (1-31): "))
            if checkinday <=0 or checkinday > 31:
                raise DateException("Day number should be be betwwen  1 and 31")
            
    
            checkinmonth = int(input("Enter checkin-Month(MM) (1 - 12): "))
            if checkinmonth <=0 or checkinmonth>12:
                raise DateException("Month number should be be betwwen  1 and 12")
    
            checkinyear = int(input("Enter checkin-Year(YYY): "))
            if len(str(checkinyear)) !=4:
                raise DateException("Please Provide Valid Year")
    
            checkin = date(checkinyear,checkinmonth,checkinday)
            checkin_fmt = checkin.strftime("%d-%m-%Y")
            
            if(checkin < today):
                raise DateException("Check in day is less than today")
            if checkin > today + timedelta(days=180):
                raise DateException("Check In Date Cannot be more than 180 days from today")
            print(f"Check-In Date {checkin_fmt}")

            #Taking checkout
            checkoutday = int(input("Enter checkout-day(DD) (1-31): "))
            if checkoutday <=0 or checkoutday > 31:
                raise DateException("Day number should be be betwwen  1 and 31")
            
            checkoutmonth = int(input("Enter checkout-Month(MM) (1 - 12): "))
            if checkoutmonth <=0 or checkoutmonth>12:
                raise DateException("Month number should be be betwwen  1 and 12")
            
            checkoutyear = int(input("Enter checkout-Year(YYY): "))
            if len(str(checkoutyear)) !=4:
                raise DateException("Please Provide Valid Year")
            
            checkout = date(checkoutyear,checkoutmonth,checkoutday)

            checkout_fmt = checkout.strftime("%d-%m-%Y")
            if(checkout <= checkin):
                raise DateException("Check out should be greater than Check in")

            nights = (checkout - checkin).days
            if(nights> 30):
                raise BookingException("Stay Cannot be more than 30 nights")
            
            print(f"Check-Out Date {checkout_fmt}")

            break
    
    
    
        except DateException as e:
            print(e)
        except BookingException as e:
            print(e)
    
        except ValueError:
            print("Please Enter Valid input")

    available_rooms = check_available_rooms(roomtype,guests,checkin_fmt,checkout_fmt)

    

    if not available_rooms :
        print(f"No Suitable Roomtype; {roomtype} available")
        alternative_rooms = see_alternative_rooms(roomtype,guests,checkin_fmt,checkout_fmt)

        if alternative_rooms:
            print("-----Alternative Rooms-----")
            for rtype,rooms in alternative_rooms.items():
                print(f"{rtype} : {rooms}")
                print("Please Choose Another Room Type...")
            return
        else:
            print("No Suitable Alternative Available too...")
        return
        
    allocated_room = available_rooms[0]
   
    booking_object = bk(name,phone,email,guests,roomtype,allocated_room,checkin_fmt,checkout_fmt)

    #Status of booking
    bk_status = booking_object.status

    #----------------------------Calculating Bill------------------------
    cursor.execute('''Select count(*) from Bookings Where Phone_Number = ? and Status = ?''',(phone,'CHECKED_OUT'))
    row = cursor.fetchone()
    completed_stays = row[0]
    rtype_obj = room_type_obs[allocated_room]
    
    final_bill = calculate_final_bill(checkin,checkout,rtype_obj,guests,completed_stays)

    #inserting data into bookings table
    query = "insert into bookings(Guest_Name,Phone_Number,Email,No_of_Guests,Check_In,Check_Out,Room_id,Status) Values(?,?,?,?,?,?,?,?)"

    
   

    # bk.bookings[bkid] = booking_object
    
    # booking_object.bookingid = bkid

    try:
        cursor.execute(
    "SELECT Phone_Number FROM Guests WHERE Phone_Number = ?",
    (phone,)
    )
        guest_data = cursor.fetchone()

        if guest_data is None:
            cursor.execute("""
        INSERT INTO Guests (Guest_Name, Phone_Number, Email)
        VALUES (?, ?, ?)
        """, (name, phone, email))

        

        cursor.execute(query,(name,phone,email,guests,checkin_fmt,checkout_fmt,allocated_room,bk_status))
            # print("Booking Confirmed..Thank You")
        bkid = cursor.lastrowid

        for n in final_bill["night_details"]:
            cursor.execute("""
                INSERT INTO Booking_Nightly_Charges
                (Booking_Id, Stay_Date, Day_Name, Room_Tariff,
                Extra_Guest_Charge, GST_Rate, GST_Amount,
                Night_Total, Discount, Discounted_Amount, Total_Rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bkid,
                n["stay_date"],
                n["day_name"],
                n["room_tarrif"],
                n["extra_guest_charge"],
                n["gst_rate"],
                n["gst_amount"],
                n["night_total"],
                n["discount"],
                n["discount_amount"],
                n["final_night_charge"]
            ))
            

        cursor.execute("""
        INSERT INTO Booking_Billing_Summary
        (Booking_Id, Total_Charges, Long_Stay_Discount,
        Loyalty_Discount, Total_Discount, Taxable_Amount,
        Total_GST, Final_Amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
        bkid,
        final_bill["total_charges"],
        final_bill["long_stay_discount"],
        final_bill["loyalty_discount"],
        final_bill["total_discount"],
        final_bill["total_amount_after_disc"],
        final_bill["total_gst_amount"],
        final_bill["final_amount"]
        ))

        conn.commit()
        booking_object.bookingid = bkid
        bk.bookings[bkid] = booking_object
        print("Booking Confirmed...Thank you")
    except sqlite3.Error as e:
        conn.rollback()
        print("Booking Failed:", e)
        return
        
    

    nights = final_bill["night_details"]

    print(f"Stay_Date    Day_Name   Room_Tarrif  Extra_Guest_Charge  GST_Rate  Final_Amount ")
    for n in nights:
        print(f"{n["stay_date"]:<12} {n["day_name"]:<10} {n["room_tarrif"]:<12} {n["extra_guest_charge"]:<19} {n["gst_rate"]*100:<10} {n["final_night_charge"]:<9}")

    bill_amount = round(final_bill["final_amount"],2)
    gst_amount = final_bill["total_gst_amount"]
    long_stay_disc = final_bill["long_stay_discount"]
    loyalty_disc = final_bill["loyalty_discount"]
    total_charges = final_bill["total_charges"]
    total_disc = final_bill["total_discount"]

    print(f"\nTotal Charges: {total_charges}")
    print(f"Long Stay Discount: {long_stay_disc}")
    print(f"Loyalty Discount: {loyalty_disc}")
    print(f"Total Discount Amount: {total_disc}")
    print(f"Gst Amount: {gst_amount}")
    print(f"Total Bill: {bill_amount}")

    print()
    show_table("Bookings")
    
    #---------------------------------------------------------------------------------
    # query = cursor.execute("Select Booking_Id from Bookings ")
    # data = cursor.fetchall()
    # for row in data:
    #     bk.bookings[row[0]] = booking_object


    #storing in dictionary
    # bk.bookings[booking_object.bookingid] = booking_object
    # print()
    # for bookings in bk.bookings.values():
    #     print(bookings)

#Checking In
def check_in():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    print("-----------Check In----------------")


    try:

        booking_id = int(input("Enter Booking Id: "))
        cursor.execute("Select Booking_Id,Check_In,Check_Out,Status from Bookings Where Booking_Id = ?",(booking_id,))

        booking_data = cursor.fetchone()

        if booking_data is None:
            print("Booking Not Found...")

        check_in = booking_data[1]
        check_out = booking_data[2]
        Status = booking_data[3]

        if Status == "CANCELLED":
            raise InvalidStatusException("Booking Cancelled,You Cannot Check In")
        if Status == "CHECKED_OUT":
            raise InvalidStatusException("Cannot Check In,Guest ALready Checkout")
        if Status == "CHECKED_IN":
            raise InvalidStatusException("Guest Already Checked in")
        if Status != "CONFIRMED":
            raise InvalidStatusException("Inavlid Booking Status")

        today = date.today()
        check_in_fmt = datetime.strptime(check_in,"%d-%m-%Y").date()
        check_out_fmt = datetime.strptime(check_out,"%d-%m-%Y").date()

        if check_in_fmt < today:
            raise DateException("Check In Date less than today")

        cursor.execute("""
            UPDATE Bookings
            SET Status = 'CHECKED_IN'
            WHERE Booking_Id = ?
        """, (booking_id,))

        print(f"Booking ID with {booking_id} changed to CHECKED_IN")

        conn.commit()    

    except (InvalidStatusException,DateException) as e:
        print(e)
    except ValueError as e:
        print(e)


#Checking out
def check_out():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()
    print("-----Guest Checking Out-----")
    room_types = room_type_obs

    #gettting booking record based on booking id
    try:
        booking_id = int(input("Enter the Booking Id: "))

        cursor.execute("Select Guest_Name,Phone_Number,Email,No_of_Guests,Check_In,Check_Out,Room_id,Status from Bookings Where Booking_Id = ?",(booking_id,))

        booking_det = cursor.fetchone()

        if booking_det is None:
            print("No Booking Found")
            return

        print(booking_det)
    
        guest_name = booking_det[0]
        phone = booking_det[1]
        email = booking_det[2]
        guests = booking_det[3]
        check_in = booking_det[4]
        check_out = booking_det[5]
        roomno = booking_det[6]        
        check_in_fmt = datetime.strptime(check_in,"%d-%m-%Y").date()       
        check_out_fmt = datetime.strptime(check_out,"%d-%m-%Y").date()
        
        roomtypeobj = room_type_obs[roomno]
        status = booking_det[7]

        if status == "CHECKED_OUT":
            print("Guest Already Checked Out...")
            return

        if status == "CONFIRMED":
            print("Guest need to check in first...")
            return

        if status != "CHECKED_IN":
            raise InvalidStatusException("Invalid Status..")
            return

        #Night by Night Charges
        cursor.execute("""
            SELECT Stay_Date, Day_Name, Room_Tariff,
                   Extra_Guest_Charge, Night_Total, Discount,
                   Discounted_Amount, GST_Rate, GST_Amount, Total_Rate
            FROM Booking_Nightly_Charges
            WHERE Booking_Id = ?
            ORDER BY Stay_Date
            """, (booking_id,))
        
        night_details = cursor.fetchall()

        # for row in night_details:
        #     print(row)

        print()
        

        #Booking Bill Summary
        cursor.execute("""
        SELECT Total_Charges, Long_Stay_Discount,
               Loyalty_Discount, Total_Discount,
               Taxable_Amount, Total_GST, Final_Amount
        FROM Booking_Billing_Summary
        WHERE Booking_Id = ?
        """, (booking_id,))


        bill_details = cursor.fetchone()
        # print(bill_details)

        
        generate_invoice(booking_id,night_details,bill_details)
        print("Invoice Generetaedd...")

        update_query = '''Update Bookings Set Status = "CHECKED_OUT" where Booking_Id = ? and Status = "CHECKED_IN"'''
        

        cursor.execute(update_query,(booking_id,))
        conn.commit()
        if cursor.rowcount != 1:
            raise InvalidStatusException("Unable to Update Status..")
        print("Guest Checked Out...Please Visit Us Again")

               
    except (ValueError,TypeError) as e:
        print(e)
        return 
    except(InvalidStatusException) as e:
        print(e)
        return
    except FileNotFoundError:
        print("File Not Found")
        return

#Cancellation
def cancel_booking():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()
    cursor.execute('''PRAGMA foreign_keys = ON''')

    print("========CANCEL BOOKING=========")

    try:
        bid = int(input("Enter Booking Id: "))

        cursor.execute("Select Check_In,Status from Bookings where Booking_Id = ?",(bid,))

        data = cursor.fetchone()

        if data is None:
            raise BookingException("Noo Bookings Found...")

        today = date.today()
        checkin = datetime.strptime(data[0],"%d-%m-%Y").date()

        status = data[1]

        if status == "CHECKED_OUT":
            print("Guest Already Checked Out..Cannot Cancel Booking")
            return

        if status == "CHECKED_IN":
            print("Guest Already Checked In...Cannot Cancel Booking")
            return

        if status == "CANCELLED":
            print("Booking Alredy Cancelled...")
            return

        cursor.execute(''' 
        Select Final_Amount from Booking_Billing_Summary where Booking_Id = ?
        
        ''',(bid,))
        data = cursor.fetchone()
        total_bill = data[0]


        diff_days = (checkin-today).days
        print(f"Difference betwwen today and checkin: {diff_days}")
        ref_amount = 0


        if diff_days >=7 :
            ref_amount = total_bill
            

        elif(diff_days >=2 and diff_days<7):
            ref_amount = total_bill - (total_bill*0.5)
            
        else:
            ref_amount = 0

        cursor.execute('''
        Update Bookings Set Status = ? Where Booking_Id = ? and Status = ?
        ''',("CANCELLED",bid,"CONFIRMED"))
        conn.commit()
        print("Booking Cancelled...")

        print(f"Refund Amount: {ref_amount}")

    except ValueError:
        print("Please Enter Valid Input..")
    except BookingException as e:
        print(e)
    except TypeError as e:
        print(e)
    except sqlite3.Error as e:
        print(f"DataBase Error: {e}")

#Viewing Booking Details

def view_bookings():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    print("ALL BOOKINGS")
    cursor.execute("Select * from Bookings")
    data = cursor.fetchall()

    if data is None:
        print("No bookings Found")


    for row in data:
        
        print(f'''{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]}''')

#Guest Stay History 
def guest_stay_history():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    try:
        print("-----------Guest Stay History--------------")
        phone = input("Enter Phone Number(10 digits): ")

        while len(phone) != 10 or not(phone.startswith("6") or phone.startswith("7") or phone.startswith("8") or phone.startswith("9")):
            print("Phone Number Should be 10 digits Starting With 6,7,8,9")
            phone = input("Enter Phone Number(10 digits): ")

        cursor.execute("Select Guest_Name,Phone_Number,Email from Guests Where Phone_Number = ?",(phone,))
        data = cursor.fetchone()

        if data is None:
            print("No Guest Found...")
            return

        print("-----Guest Details------")
        print(f"Guest Name: {data[0]}")
        print(f"Phone Number: {data[1]}")
        print(f"Email: {data[2]}")


        cursor.execute("Select Booking_Id, Room_id,Check_In,Check_Out,Status from Bookings Where Phone_Number = ?",(phone,))
        bdata = cursor.fetchall()

        print("\n===========Stay History===========")

        print(f"BookingId | Room_No | Check-In   | Check-Out  | Status")
        for row in bdata:
            print(f"{row[0]:<9} | {row[1]:<7} | {row[2]} | {row[3]} | {row[4]}")


    except ValueError :
        print("Please Enter Valid Input")


#Occupancy Report
def see_occupancy_report():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    try:
        start_date = input("Enter The Start Date(DD-MM-YYYY): ")
        end_date = input("Enter The End Date(DD-MM-YYYY): ")

        start = datetime.strptime(start_date,"%d-%m-%Y").date()
        end = datetime.strptime(end_date,"%d-%m-%Y").date()

        if end<=start:
            raise DateException("End Date Must be Greater than Start Date")

        cursor.execute("Select count(*) from Rooms")
        data = cursor.fetchone()
        
        
        total_rooms = data[0]
        if total_rooms == 0:
            print("No Rooms Avaialble...")
            return

        total_occ = 0
        total_days = 0
    
        curr_date = start

        while curr_date < end:
            curr_date_fmt = datetime.strftime(curr_date,"%d-%m-%Y")

            cursor.execute(''' Select Count(Distinct Room_id)
            from Bookings Where Check_In <= ? and Check_Out>?


            ''',(curr_date_fmt,curr_date_fmt))

            occupied_rooms = cursor.fetchone()[0]

            occ_rep = (occupied_rooms/total_rooms)*100
            total_occ += occ_rep
            total_days += 1

            curr_date += timedelta(days=1)

        avg_occ = total_occ/total_days

        print("=====OCCUPANCY REPORT===========")
        print(f"Total Rooms: {total_rooms}")
        print(f"Total Days: {total_days}")
        print(f"Average_Occupancy: {round(avg_occ,2)}")


    except DateException as e:
        print(e)

    except ValueError :
        print("Please Enter Valid Input")
    except sqlite3.Error as e:
        print(f"Database Error: {e}")


#Revenue Report
def revenue_report():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    cursor.execute('''Select r.Room_Type,Count(b.Booking_Id),COALESCE(Sum(bs.Taxable_Amount),0),COALESCE(Sum(bs.Total_GST),0)from Rooms r Left Join Bookings b on r.Room_id = b.Room_id and b.Status = "CHECKED_OUT" Left Join Booking_Billing_Summary bs on b.Booking_Id = bs.Booking_Id group by r.Room_Type''')

    data = cursor.fetchall()

    print(f"================== Revenue Report ================")

    print(f"Room_Type  |  Stays  |  Ttoal_Amount  |  Totoal_GST")
    print("--------------------------------------------------")

    for row in data:
        roomtype = row[0]
        stays = row[1]
        toat_amount = row[2]
        toat_gst = row[3]

        print(f"{roomtype:<9}  |  {stays:<5}  |  {toat_amount:<12}  |  {toat_gst}")

    conn.close()

#Exporting Bookings
def export_bookings():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    try:
        with open("bookings.csv","w") as file:
            file.write(f"============== Booking Details ====================\n")
            file.write(f"Booking_Id | Guest Name | Phone_Number |  Email  | Guests | Check_In | Check_Out | Room_id | Status \n ")

            cursor.execute("Select * from Bookings")
            data = cursor.fetchall()

            for row in data:
                bid = row[0]
                gname = row[1]
                phone = row[2]
                email = row[3]
                guests = row[4]
                checkin = row[5]
                checkout = row[6]
                roomno = row[7]
                status = row[8]

                file.write(f"{bid}  |  {gname}  | {phone} |  {email}  |  {guests} | {checkin} | {checkout} | {roomno} | {status}\n")

            print("bookings.csv generated successfully")
    except FileNotFoundError:
        print("File Not Found")
    except sqlite3.Error :
        print("Issue From Database...")

    
#Entry Point 
def start_program():

#     conn = sqlite3.connect("stayeasy.db")
#     cursor = conn.cursor()
#     cursor.execute(''' Select Total_Rate From Booking_Nightly_Charges;''')
# #     
    
    
# #     cursor.execute('''Delete FROM Booking_Nightly_Charges
# # WHERE Booking_Id = 11;''')
# #     conn.commit()

    
# #     print("Data Deleted Successfully")
# #     # cursor.execute("PRAGMA table_info(Booking_Nightly_Charges)")
#     data = cursor.fetchall()

#     for row in data:
#         print(row)
    

    
    
#     conn.close()
    
    #-------------------------------
    global room_type_obs
    # print()
    create_tables()
    print()
    room_type_obs = load_rooms()

    # check_out()
    # cancel_booking()
    # show_table("Bookings")
    # view_bookings()

    # guest_stay_history()
    # see_occupancy_report()
    # revenue_report()
    print()
    # show_table("Bookings")
    print()
    # export_bookings()

    

    while True:
        print("\n1.Search Room Availability\n2.Create Booking\n3.Check-In\n4.Check-Out\n5.Cancel Booking\n6.View Bookings\n7.Guest Stay histry\n8.Occupancy Report\n9.Revenue Report\n10.Export All Bookings To CSV\n11.Exit\n")
        try:
            choice = int(input("Enter your Choice: "))

            while choice < 0 or choice > 11:
                print("Please Enter Valid Choice(1-11)")
                choice = int(input("Enter your Choice: "))
            if choice == 1:
                roomtype = input("Enter Room Type(Standard/Deluxe/Suite): ").strip().upper()
                while roomtype not in ["STANDARD","DELUXE","SUITE"]:
                    print("Please Select Valid Rooms")
                    roomtype = input("Enter Room Type(Standard/Deluxe/Suite): ").strip().upper()

                guests = int(input("Enter no.of guests: "))

                while guests<1:
                    print("Guests Should be greater than 0")
                    guests = int(input("Enter no.of guests: "))

                checkin = input("Enter Check-In Date(DD-MM-YYYY): ")
                checkin_fmt = datetime.strptime(checkin,"%d-%m-%Y").date()

                checkout = input("Enter Check-Out Date(DD-MM-YYYY): ")
                checkout_fmt = datetime.strptime(checkout,"%d-%m-%Y").date()

                check_available_rooms(roomtype,guests,checkin,checkout)
                print()

            elif choice == 2:
                make_booking()
            elif choice == 3:
                check_in()
            elif choice == 4:
                check_out()
            elif choice == 5:
                cancel_booking()
            elif choice == 6:
                view_bookings()
            elif choice == 7:
                guest_stay_history()
            elif choice == 8:
                see_occupancy_report()
            elif choice == 9:
                revenue_report()
            elif choice == 10:
                export_bookings()
            else:
                print("Exiting....")
                break
            
            

        except ValueError:
            print("Please Enter Valid Input ")
    # show_table("Booking_Nightly_Charges")
    # print()
    # show_table("Booking_Billing_Summary")


start_program()



