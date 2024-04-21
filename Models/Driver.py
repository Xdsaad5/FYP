class Driver:
    def __init__(self, n, e, c, veh):
        self.name = n
        self.email = e
        self.contact = c
        self.vehicle = veh
        if veh.lower() == 'car':
            self.total_seats = 4
        else:
            self.total_seats = 2

    def dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'contact': self.contact,
            'vehicle': self.vehicle,
            'total_seats': self.total_seats
        }
