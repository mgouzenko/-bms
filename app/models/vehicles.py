from sqlalchemy.sql import text

class vehicles(object):
    def __init__(self, state, plate_num, make, model, color, is_requested,
            key_number, spot_number, default_spot, building_id):
        self.state = state
        self.plate_num = plate_num
        self.make = make
        self.model = model
        self.color = color
        self.is_requested = is_requested
        self.key_number = key_number
        self.spot_number = spot_number
        self.default_spot = default_spot
        self.building_id = building_id
        self.drivers = None

    def get_drivers(self, database_connection):
        if self.drivers:
            return self.drivers
        query = """SELECT entrant_id
                   FROM entrants NATURAL JOIN drives NATURAL JOIN vehicles
                   WHERE state = :s and plate_num = :pn"""
        cursor = database_connection.execute(
                text(query), s=self.state, pn=self.plate_num)
        from entrants import entrants
        self.drivers = [entrants.find_by_id(entrant_id[0], database_connection)
                        for entrant_id in cursor]
        return self.drivers

    @staticmethod
    def find_by_spot(database_connection, building_id, spot):
        query = """SELECT state, plate_num, make, model, color, is_requested,
                          key_number, spot_number, default_spot, building_id
                   FROM parking_spots natural join vehicles
                   WHERE building_id = :bid and spot_number = :snum"""
        cursor = database_connection.execute(
                text(query), bid=building_id, snum=spot)
        result = cursor.fetchone()
        return vehicles(*result) if result else None

    @staticmethod
    def find_requested_cars(database_connection, building_id):
        query = """SELECT state, plate_num, make, model, color, is_requested,
                          key_number, spot_number, default_spot, building_id
                   FROM parking_spots natural join vehicles
                   WHERE building_id = :bid and is_requested = TRUE"""

        cursor = database_connection.execute(
                text(query), bid=building_id)

        return [vehicles(*result) for result in cursor]


    @staticmethod
    def find_by_license_plate(database_connection, state, license_plate):
        query = query = """SELECT state, plate_num, make, model, color, is_requested,
                                  key_number, spot_number, default_spot, building_id
                           FROM parking_spots natural join vehicles
                           WHERE state = :state and plate_num = :plate_num"""
        cursor = database_connection.execute(
            text(query), state=state, plate_num=license_plate)

        result = cursor.fetchone()
        return vehicles(*result) if result else None
