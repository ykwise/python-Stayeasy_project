from datetime import timedelta,datetime
from models.room import StandardRoom,DeluxeRoom,SuiteRoom,RoomType
def calculate_final_bill(checkin,checkout,roomtype,guests,stays):
    curr_date = checkin
    night_details = []
    total_charge = 0

    while curr_date < checkout:
        day_name = curr_date.strftime("%A")
        
        

        # print(f"{datetime.strftime(curr_date,"%d-%m-%Y")} : {day_name}")

        room_tarrif = roomtype.get_tarrif()
        if day_name in ["Friday","Saturday"]:
            room_tarrif += room_tarrif*0.2
        extra_guests = max(0,guests-2)
        extra_guest_charges = roomtype.get_extra_guest_charges() * extra_guests
        night_charge = room_tarrif + extra_guest_charges
        total_charge += night_charge
        night_details.append(
            {
                "stay_date" : datetime.strftime(curr_date,"%d-%m-%Y"),
                "day_name" : day_name,
                "room_tarrif" : round(room_tarrif,2),
                "extra_guest_charge" : round(extra_guest_charges,2),
                "night_total" : round(night_charge,2)
            }
        )
        curr_date += timedelta(days=1)

    #Now We have to calculate discounts
    longstay_disc = 0
    loyalty_disc = 0
    if len(night_details) >=7:
        longstay_disc = round(total_charge * 0.1,2)

    amount_after_lsd = round(total_charge - longstay_disc,2)

    if stays >=3 :
        loyalty_disc = amount_after_lsd * 0.05

    # amount_after_ltydisc = amount_after_lsd - loyalty_disc
    total_discount = round(longstay_disc + loyalty_disc,2)

    #distributing discount amount proption to each night
    for night in night_details:
       prop =  night["night_total"]/total_charge if total_charge else 0
       disc = round(total_discount * prop,2)
       disc_amount = round(night["night_total"] - disc,2)

       if(night["room_tarrif"] <= 7500):
           gst_rate = 0.12
       else:
           gst_rate = 0.18

       gst_amount = round(disc_amount * gst_rate,2)
       upd_amount = round(disc_amount+gst_amount,2)

       night["discount"] = disc
       night["discount_amount"] = disc_amount
       night["gst_rate"] = gst_rate
       night["gst_amount"] = gst_amount
       night["final_night_charge"] = upd_amount


    #Calculating Bill
    total_amount_after_disc = round(sum(n["discount_amount"]for n in night_details),2)
    total_gst_amount = round(sum(n["gst_amount"]for n in night_details),2)
    total_nights_charges =round(sum(n["final_night_charge"] for n in night_details),2)

    return {
        "night_details" : night_details,
        "total_charges" : total_charge,
        "long_stay_discount" : longstay_disc,
        "loyalty_discount" : loyalty_disc,
        "total_discount" : total_discount,
        "total_amount_after_disc" : total_amount_after_disc,
        "total_gst_amount" : total_gst_amount,
        "final_amount" : total_nights_charges

    }


        
        


       
       




    
    


    
    # return night_details


# #test
# checkin = datetime.strptime("11-11-2026","%d-%m-%Y").date()
# checkout = datetime.strptime("15-11-2026","%d-%m-%Y").date()

# rtype = DeluxeRoom()
# final_bill = calculate_final_bill(checkin,checkout,rtype,3,8)
# #print(r)

# nights = final_bill["night_details"]

# print(f"Stay_Date    Day_Name   Room_Tarrif  Extra_Guest_Charge  GST_Rate  Final_Amount ")
# for n in nights:
    
#     # print(n)
#     print(f"{n["stay_date"]:<12} {n["day_name"]:<10} {n["room_tarrif"]:<12} {n["extra_guest_charge"]:<19} {n["gst_rate"]*100:<10} {n["final_night_charge"]:<9}")


# bill_amount = round(final_bill["final_amount"],2)
# gst_amount = final_bill["total_gst_amount"]
# long_stay_disc = final_bill["long_stay_discount"]
# loyalty_disc = final_bill["loyalty_discount"]
# total_charges = final_bill["total_charges"]
# total_disc = final_bill["total_discount"]

# print(f"\nTotal Charges: {total_charges}")
# print(f"Long Stay Discount: {long_stay_disc}")
# print(f"Loyalty Discount: {loyalty_disc}")
# print(f"Total Discount Amount: {total_disc}")
# print(f"Gst Amount: {gst_amount}")
# print(f"Total Bill: {bill_amount}")
