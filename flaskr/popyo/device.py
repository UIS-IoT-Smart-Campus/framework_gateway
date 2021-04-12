

class Device():

    def __init__(self):
        self.id = None
        self.tag = None
        self.name = None
        self.device_type = None
        self.description = None
    
    def set_data(self,tag,name,device_type,description):
        self.tag = tag
        self.name = name
        self.device_type = device_type
        self.description = description
    

    def set_cursor(self,cursor):
        if cursor:
            self.id = cursor[0]
            self.tag = cursor[1]
            self.name = cursor[2]
            self.device_type = cursor[3]
            self.description = cursor[4]


    