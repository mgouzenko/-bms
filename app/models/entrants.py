from sqlalchemy.sql import text
from vehicles import vehicles

class entrants(object):
    def __init__(self,
            entrant_id=None,
            fname=None,
            lname=None,
            age=None,
            username=None,
            password=None,
            phone_num=None,
            building_id=None):
        self.entrant_id = entrant_id
        self.fname = fname
        self.lname = lname
        self.age = age
        self.username = username
        self.password = password
        self.phone_num = phone_num
        self.building_id = building_id

    @staticmethod
    def add_as_driver(state, plate_num, building_id, entrant_id,
            database_connection):
        car = vehicles.find_by_license_plate(database_connection,
                                             state, plate_num, building_id)
        if not car:
            return False

        drivers = car.get_drivers(database_connection)
        for driver in drivers:
            if driver.entrant_id == entrant_id:
                return True

        query = """INSERT INTO drives
                        (entrant_id, building_id, plate_num, state)
                   VALUES (:eid, :bid, :plate_num, :state)"""
        database_connection.execute(text(query),
                                    eid=entrant_id,
                                    bid=building_id,
                                    plate_num=plate_num,
                                    state=state)
        return True

    @staticmethod
    def search_by_name(fname, lname, building_id, database_connection):
        search_predicates = ['building_id = :building_id']
        search_attrs = {'building_id': building_id}

        if not fname and not lname:
            return []

        if fname:
            search_attrs['fname'] = fname
            search_predicates.append('fname = :fname')

        if lname:
            search_attrs['lname'] = lname
            search_predicates.append('lname = :lname')

        query = """SELECT entrant_id, fname, lname, age,
                          username, password, phone_num,
                          building_id
                   FROM entrants NATURAL JOIN of_a
                   WHERE {}""".format(' AND '.join(search_predicates))

        print query

        cursor = database_connection.execute(text(query), **search_attrs)
        return [entrants(*result) for result in cursor]

    def put(self, database_connection):
        if self.entrant_id is not None:
            self.update()
            return

        put_attrs = ['fname', 'lname', 'age', 'username', 'password',
                     'phone_num']

        place_holders = map(lambda a: ':{}'.format(a), put_attrs)

        colnames = ', '.join(put_attrs)
        values = ', '.join(place_holders)

        query = """INSERT INTO entrants ({colnames})
                   VALUES ({values}) RETURNING entrant_id
                   """.format(colnames=colnames, values=values)

        real_values = { attr:getattr(self, attr) for attr in put_attrs}
        ids = database_connection.execute(
                text(query),
                **real_values)

        self.entrant_id = ids.fetchone()[0]

    def update(self):
        pass

    @staticmethod
    def find_by_username(username, database_connection):
        query = """SELECT entrant_id, fname, lname, age,
                          username, password, phone_num,
                          building_id
                   FROM entrants NATURAL JOIN of_a
                   WHERE entrants.username = :name"""
        cursor = database_connection.execute(text(query), name=username)
        result = cursor.fetchone()
        if result is None:
            return result
        return entrants(*result)

    @staticmethod
    def find_by_id(entrant_id, database_connection):
        query = """SELECT entrant_id, fname, lname, age,
                          username, password, phone_num,
                          building_id
                   FROM entrants NATURAL JOIN of_a
                   WHERE entrant_id = :id"""
        cursor = database_connection.execute(text(query), id=str(entrant_id))
        result = cursor.fetchone()
        if result is None:
            return result
        return entrants(*result)

class admins(entrants):

    @staticmethod
    def find_by_username(username, database_connection):
        query = """SELECT entrant_id, fname, lname, age,
                          username, password, phone_num,
                          building_id
                    FROM entrants NATURAL JOIN admins NATURAL JOIN of_a
                    WHERE username = :name"""
        cursor = database_connection.execute(text(query), name=username)
        result = cursor.fetchone()
        if result is None:
            return None
        return admins(*result)

    @staticmethod
    def find_by_id(admin_id, database_connection):
        query = """SELECT entrant_id, fname, lname, age,
                          username, password, phone_num,
                          building_id
                   FROM entrants NATURAL JOIN admins NATURAL JOIN of_a
                   WHERE entrant_id = :eid"""
        cursor = database_connection.execute(text(query), eid=admin_id)
        result = cursor.fetchone()
        if result is None:
            return None
        return admins(*result)

class unit_entrants(entrants):
    def __init__(self, unit_id, building_id, *args, **kwargs):
        super(unit_entrants, self).__init__(*args, **kwargs)
        self.unit_id=unit_id
        self.building_id=building_id

    def put(self, database_connection):
        skip_insertion = False
        if self.entrant_id != None:
            skip_insertion = True
            self.update()
        super(unit_entrants, self).put(database_connection)

        if not skip_insertion:
            query = """INSERT INTO of_a (building_id, entrant_id)
                       VALUES (:building_id, :entrant_id)"""
            database_connection.execute(text(query),
                                        building_id=self.building_id,
                                        entrant_id=self.entrant_id)

            query = """INSERT INTO unit_entrants (unit_id, building_id, entrant_id)
                       VALUES (:unit_id, :building_id, :entrant_id)"""
            database_connection.execute(text(query),
                                        unit_id=self.unit_id,
                                        building_id=self.building_id,
                                        entrant_id=self.entrant_id)

class guests(unit_entrants):

    @staticmethod
    def delete_by_id(guest_id, database_connection):
        query = """DELETE FROM guests WHERE guests.entrant_id = :gid"""
        database_connection.execute(text(query), gid=guest_id)

    def put(self, database_connection):
        skip_insertion = False
        if self.entrant_id != None:
            skip_insertion = True
            self.update()
        super(guests, self).put(database_connection)

        if not skip_insertion:
            query = """INSERT INTO guests (entrant_id)
                       VALUES (:entrant_id)"""
            database_connection.execute(text(query), entrant_id=self.entrant_id)

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
        query = """SELECT state, plate_num, make, model, color, is_requested,
                          key_number, spot_number, default_spot, building_id
                   FROM unit_entrants NATURAL JOIN drives NATURAL JOIN vehicles
                   WHERE building_id = :bid and unit_id = :uid
                   """
        print self.building_id
        cursor = database_connection.execute(
                text(query), bid=self.building_id, uid=self.unit_id)

        cars = [ vehicles(*result) for result in cursor]
        return cars
