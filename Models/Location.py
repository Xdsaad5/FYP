class Location:
    def __init__(self,start_location,end_location):
        self.stat_loc = start_location
        self.end_loc = end_location

    def dict(self):
        return {
            'start': self.stat_loc,
            'end': self.end_loc
        }