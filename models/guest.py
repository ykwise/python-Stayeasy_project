class Guest:
    guests = {}
    def __init__(self,name,phone,email):
        self.name = name
        self.phone = phone
        self.email = email

    def __str__(self):
        return f"Guest Name: {self.name} | Phone: {self.phone} | Email : {self.email}"
