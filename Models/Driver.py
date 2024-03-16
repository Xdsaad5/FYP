class Driver:
    def __init__(self, n, e, c, veh):
        self.name = n
        self.email = e
        self.contact = c
        self.vehicle = veh
        if veh.lower() == 'car':
            self.available_seats = 4
        else:
            self.available_seats = 2

    def dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'contact': self.contact,
            'vehicle': self.vehicle,
            'seats': self.available_seats
        }
