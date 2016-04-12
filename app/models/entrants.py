from sqlalchemy.sql import text

class entrants(object):
    def __init__(self, entrant_id, fname, lname, age, username, password, phone_num):
        self.id = entrant_id
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
    @staticmethod
    def find_by_id(entrant_id, database_connection):
        entrant = super(residents, residents).find_by_id(
                entrant_id, database_connection)
        if entrant:
            query = "SELECT * FROM residents WHERE residents.entrant_id = :id"
            cursor = database_connection.execute(text(query), id=entrant_id)
            if cursor:
                return entrant

        return None
