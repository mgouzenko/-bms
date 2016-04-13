from sqlalchemy.sql import text
from vehicles import vehicles

class service_providers(object):
    def __init__(self, business_id, business_name, business_description,
            phone_num, email):
        self.business_id = business_id
        self.business_name = business_name
        self.business_description = business_description
        self.phone_num = phone_num
        self.email = email

    @staticmethod
    def find_by_email(email, database_connection):
        query = """SELECT business_id, business_name, business_description,
                          phone_num, email
                   FROM service_providers
                   WHERE service_providers.email = :email"""
        cursor = database_connection.execute(text(query), email=email)
        result = cursor.fetchone()
        if result is None:
            return None
        return service_providers(*result)

    @staticmethod
    def find_by_id(business_id, database_connection):
        query = """SELECT business_id, business_name, business_description,
                          phone_num, email
                   FROM service_providers
                   WHERE service_providers.business_id = :bid"""
        cursor = database_connection.execute(text(query), bid=business_id)
        result = cursor.fetchone()
        if result is None:
            return None
        return service_providers(*result)
