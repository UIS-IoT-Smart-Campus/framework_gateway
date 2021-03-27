

class Device():

    def __init__(self):
        self.id = None
        self.tag = None
        self.device_name = None
        self.device_description = None
    

    def set_cursor(self,cursor):
        if cursor:
            self.id = cursor[0]
            self.tag = cursor[1]
            self.name = cursor[2]
            self.description = cursor[3]


    