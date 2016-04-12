from sqlalchemy.sql import text
from vehicles import vehicles

class entrants(object):
    def __init__(self, entrant_id, fname, lname, age, username, password, phone_num):
        self.entrant_id = entrant_id
        self.fname = fname
        self.lname = lname
        self.age = age
        self.username = username
        self.password = password
        self.phone_num = phone_num

    @staticmethod
    def find_by_username(username, database_connection):
        query = "SELECT * FROM entrants WHERE entrants.username = :name"
        cursor = database_connection.execute(text(query), name=username)
        result = cursor.fetchone()
        if result is None:
            return result
        return entrants(*result)

    @staticmethod
    def find_by_id(entrant_id, database_connection):
        query = "SELECT * FROM entrants WHERE entrants.entrant_id = :id"
        cursor = database_connection.execute(text(query), id=entrant_id)
        result = cursor.fetchone()
        if result is None:
            return result
        return entrants(*result)

class residents(entrants):
    def __init__(self, entrant_id, fname, lname, age, username, password,
                 phone_num, unit_id, building_id):

        super(residents, self).__init__(
                entrant_id, fname, lname, age, username, password, phone_num)
        self.unit_id = unit_id
        self.building_id = building_id

    @staticmethod
    def find_by_id(entrant_id, database_connection):
        query = """SELECT entrant_id, fname, lname, age, username, password,
                          phone_num, unit_id, building_id
                   FROM residents NATURAL JOIN unit_entrants NATURAL JOIN entrants
                   WHERE entrant_id = :id"""
        cursor = database_connection.execute(text(query), id=entrant_id)
        result = cursor.fetchone()
        if result is None:
            return None
        return residents(*result)

    def get_guests(self, database_connection):
        query = """SELECT entrant_id, fname, lname, age, username, password,
                          phone_num
                   FROM entrants NATURAL JOIN unit_entrants NATURAL JOIN guests
                   WHERE building_id = :bid and unit_id = :uid
                   """
        cursor = database_connection.execute(
                text(query), bid=self.building_id, uid=self.unit_id)
        return [ entrants(*row) for row in cursor ]

    def get_cars(self, database_connection):
        query = """SELECT spot_number
                   FROM units NATURAL JOIN owns NATURAL JOIN parking_spots
                   WHERE building_id = :bid and unit_id = :uid
                   """
        cursor = database_connection.execute(
                text(query), bid=self.building_id, uid=self.unit_id)

        cars = [ vehicles.find_by_spot(
                    database_connection,
                    self.building_id,
                    spot[0]) for spot in cursor]
        return cars
