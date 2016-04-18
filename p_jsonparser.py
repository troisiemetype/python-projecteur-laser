class JsonParser:
    
    #This is the init function    
    def __init__(self):
        pass
    
    #This function creates a json string from the coordinates
    def to_json(self, pix_id, x_pos, y_pos, l_pos, speed=200, mode = 0):
        json_string = '{{"ID":{0},"X":{1},"Y":{2},"L":{3},"speed":{4},"mode":{5}}}\n'
        json_string = json_string.format(pix_id, x_pos, y_pos, l_pos,speed, mode)
        return json_string
    
    #This function split the json chain received from the arduino into vars.
    def from_json(self, json):
        pass