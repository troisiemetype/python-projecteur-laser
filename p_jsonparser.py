import json

class JsonParser(json.JSONEncoder, json.JSONDecoder):
    
    #This is the init function    
    def __init__(self):
        json.JSONEncoder.__init__(self, sort_keys = True, separators=(',', ':'))
        json.JSONDecoder.__init__(self)
        
    
    #This function creates a json string from the coordinates
    def to_json(self, pix_id, x_pos, y_pos, l_pos, speed=200, mode = 0):
        json_data = {"ID":pix_id,"X":x_pos,"Y":y_pos,"L":l_pos,"speed":speed,"mode":mode}
        json_string = self.encode(json_data)
        json_string += '\n'
        return json_string
    
    #This function split the json chain received from the arduino into vars.
    def from_json(self, json):
        try:
            dict_data = self.decode(json)
            return dict_data
        except ValueError as error:
            return error 
        
        