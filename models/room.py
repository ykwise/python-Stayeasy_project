#Room Type Classes
from abc import ABC,abstractmethod
class RoomType(ABC):
    @abstractmethod
    def get_tarrif(self):
        pass

    @abstractmethod
    def get_max_guests(self):
        pass
    @abstractmethod
    def get_extra_guest_charges(self):
        pass

    @abstractmethod
    def get_gst(self):
        pass

    @abstractmethod
    def is_breakfast(self):
        pass

#StandardRoon
class StandardRoom(RoomType):
    def __init__(self):
        self.roomtype = "Standard"
        self.baseamount = 2500
        self.max_guests = 2
        self.extra_guest_charges = 0
        
    def get_tarrif(self):
        return self.baseamount

    def get_max_guests(self):
        return self.max_guests

    def get_extra_guest_charges(self):
        return self.extra_guest_charges

    def get_gst(self):
        return 12

    def is_breakfast(self):
        return False

#Deluxe Room
class DeluxeRoom(RoomType):
    def __init__(self):
        self.roomtype = "Deluxe"
        self.baseamount = 4000
        self.max_guests = 3
        self.extra_guest_charges = 800

    def get_tarrif(self):
        return self.baseamount
    
    def get_max_guests(self):
        return self.max_guests
    
    def get_extra_guest_charges(self):
        return self.extra_guest_charges
    
    def get_gst(self):
        return 12
    
    def is_breakfast(self):
        return True
#Suite Room
class SuiteRoom(RoomType):
    def __init__(self):
        self.roomtype = "Suite"
        self.baseamount = 7500
        self.max_guests = 4
        self.extra_guest_charges = 800
    def get_tarrif(self):
        return self.baseamount
    
    def get_max_guests(self):
        return self.max_guests
    
    def get_extra_guest_charges(self):
        return self.extra_guest_charges
    
    def get_gst(self):
        return 18
    
    def is_breakfast(self):
        return True

# room1 = StandardRoom()
# print(room1.get_tarrif())
# print(room1.get_extra_guest_charges())
# print(room1.get_max_guests())
# print(room1.is_breakfast())
# print("-------------")
# room2 = DeluxeRoom()

# print(room2.get_tarrif())
# print(room2.get_extra_guest_charges())
# print(room2.get_max_guests())
# print(room2.is_breakfast())
# print("------------------")
# room3 = SuiteRoom()
# print(room3.get_tarrif())
# print(room3.get_extra_guest_charges())
# print(room3.get_max_guests())
# print(room3.is_breakfast())
