import json

class JsonParser(json.JSONEncoder, json.JSONDecoder):
    
    #This is the init function    
    def __init__(self):
        json.JSONEncoder.__init__(self, sort_keys = True, separators=(',', ':'))
        json.JSONDecoder.__init__(self)
        
    
    #This function creates a json string from the coordinates
    def to_json(self, data):
        json_string = self.encode(data)
        json_string += '\n'
        return json_string
    
    #This function split the json chain received from the arduino into vars.
    def from_json(self, json):
        try:
            dict_data = self.decode(json)
            return dict_data
        except ValueError as error:
            return error 
        
        