def generate_invoice(bookingid,night_details,bill_details):

    filename = f"invoices/BK{bookingid:04d}.txt"

    with open(filename,"w") as file:
        file.write(f"======Night by Night Charges=====\n")
        for n in night_details:
            
            file.write(f"Date  |  Day  |  Room_Tarrif |  Extra_Guest_Charge |  GST_Rate  | Total_Rate\n")
            file.write(f"{n[0]}  |  {n[1]}  |  {n[2]}  |  {n[3]}  |  {n[7]}  |  {n[9]}  \n")

        file.write(f"==========Bill Summary===========\n")
        file.write(f"Total_Charges: {bill_details[0]}\n")
        file.write(f"Long_Stay_Discount: {bill_details[1]}\n")
        file.write(f"Loyalty_Discount: {bill_details[2]}\n")
        file.write(f"Total_Discount_Amount: {bill_details[3]}\n")
        file.write(f"Amount After Discount: {bill_details[4]}\n")
        file.write(f"Total GST Amount: {bill_details[5]}\n")
        file.write(f"Final Amount: {bill_details[6]}\n")




    