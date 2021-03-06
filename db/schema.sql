DROP TABLE if exists entrants CASCADE;
CREATE TABLE entrants (
	entrant_id SERIAL,
	fname VARCHAR(40),
	lname VARCHAR(40),
	age INTEGER check (age >= 0),
	username VARCHAR(20),
	password VARCHAR(20),
	UNIQUE (username),
	phone_num VARCHAR(12),
	PRIMARY KEY (entrant_id)
);

DROP TABLE if exists admins CASCADE;
CREATE TABLE admins ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES entrants
							 ON DELETE CASCADE
);

DROP TABLE if exists service_employees CASCADE;
CREATE TABLE service_employees ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES entrants
							 ON DELETE CASCADE
);

DROP TABLE if exists buildings CASCADE;
CREATE TABLE buildings (
	building_id INTEGER,
	building_name VARCHAR(40),
	phone_num VARCHAR(12),
	street_address VARCHAR(120),
	city VARCHAR(30),
	state VARCHAR(2),
	zip_code VARCHAR(5),
	email VARCHAR(120),
	PRIMARY KEY (building_id)
);

DROP TABLE if exists service_providers CASCADE;
CREATE TABLE service_providers (
	business_id INTEGER,
	business_name VARCHAR(120),
	business_description_long TEXT,
	business_description TEXT,
	phone_num VARCHAR(12),
	email VARCHAR(120) NOT NULL,
	UNIQUE(email),
	PRIMARY KEY (business_id)
);

DROP TABLE if exists works_for;
CREATE TABLE works_for (
	entrant_id INTEGER,
	business_id INTEGER,
	PRIMARY KEY (entrant_id, business_id),
	FOREIGN KEY (entrant_id) REFERENCES service_employees
							 ON DELETE CASCADE,
	FOREIGN KEY (business_id) REFERENCES service_providers
							  ON DELETE CASCADE
);

DROP TABLE if exists parking_spots CASCADE;
CREATE TABLE parking_spots ( -- parking spots within a building
	spot_number INTEGER,
	building_id INTEGER,
	spot_type VARCHAR(20) check (spot_type = 'Permanent' OR
								 spot_type = 'Temporary' OR
								 spot_type = 'Unloading'),
	PRIMARY KEY (spot_number, building_id),
	FOREIGN KEY (building_id) REFERENCES buildings ON DELETE CASCADE
);

DROP TABLE if exists vehicles CASCADE;
CREATE TABLE vehicles (
	state VARCHAR (2),
	plate_num VARCHAR(10),
	make VARCHAR(30),
	model VARCHAR(30),
	color VARCHAR(15),
	is_requested BOOLEAN,
	key_number INTEGER,
	spot_number INTEGER,
	default_spot INTEGER,
	building_id INTEGER,
	request_times TIMESTAMP ARRAY,
	UNIQUE (spot_number, building_id),
	UNIQUE (default_spot, building_id),
	UNIQUE (key_number, building_id),
	FOREIGN KEY (spot_number, building_id) REFERENCES parking_spots,
	FOREIGN KEY (default_spot, building_id) REFERENCES parking_spots,
	PRIMARY KEY (building_id, state, plate_num)
);

DROP TABLE if exists of_a CASCADE;
CREATE TABLE of_a ( -- Entrant of a building
	building_id INTEGER,
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id, building_id),
	UNIQUE(entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES entrants
							 ON DELETE CASCADE,
	FOREIGN KEY (building_id) REFERENCES buildings
							  ON DELETE CASCADE
);

DROP TABLE if exists provides_services_for;
CREATE TABLE provides_services_for ( -- buildings that service providers work in
	business_id INTEGER,
	building_id INTEGER,
	PRIMARY KEY (business_id, building_id),
	FOREIGN KEY (business_id) REFERENCES service_providers
							  ON DELETE CASCADE,
	FOREIGN KEY (building_id) REFERENCES buildings
							  ON DELETE CASCADE
);

DROP TABLE if exists drives;
CREATE TABLE drives (
	entrant_id INTEGER,
	building_id INTEGER,
	state VARCHAR (2),
	plate_num VARCHAR(10),
	PRIMARY KEY (entrant_id, building_id, state, plate_num),
	FOREIGN KEY (entrant_id) REFERENCES entrants
						     ON DELETE CASCADE,
	FOREIGN KEY (building_id, state, plate_num) REFERENCES vehicles
								   ON DELETE CASCADE
);

DROP TABLE if exists units CASCADE;
CREATE TABLE units ( -- unit within a building
	unit_id VARCHAR(6),
	floor INTEGER check (floor >= 0 AND floor < 200),
	building_id INTEGER,
	PRIMARY KEY (unit_id, building_id),
	FOREIGN KEY (building_id) REFERENCES buildings ON DELETE CASCADE
);

DROP TABLE if exists unit_entrants CASCADE;
CREATE TABLE unit_entrants ( --superclass is entrants
							 --combined with Enters relationship set
	entrant_id INTEGER,
	unit_id VARCHAR(6) NOT NULL,
	building_id INTEGER NOT NULL,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id, building_id) REFERENCES of_a,
	FOREIGN KEY (entrant_id) REFERENCES entrants
						     ON DELETE CASCADE,
	FOREIGN KEY (unit_id, building_id) REFERENCES units
									   ON DELETE CASCADE
);

DROP TABLE if exists residents;
CREATE TABLE residents ( --superclass is unit entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES unit_entrants
							 ON DELETE CASCADE
);

DROP TABLE if exists casual_entrants;
CREATE TABLE casual_entrants ( --superclass is unit entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES unit_entrants
							 ON DELETE CASCADE
);

DROP TABLE if exists guests;
CREATE TABLE guests ( --superclass is unit entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES unit_entrants
							 ON DELETE CASCADE
);

DROP TABLE if exists owns;
CREATE TABLE owns ( -- parking spot owned by a unit
	unit_id VARCHAR(6),
	spot_number INTEGER,
	building_id INTEGER,
	PRIMARY KEY (unit_id, building_id, spot_number),
	FOREIGN KEY (unit_id, building_id) REFERENCES units
									   ON DELETE CASCADE,
	FOREIGN KEY (spot_number, building_id) REFERENCES parking_spots
										   ON DELETE CASCADE
);

DROP FUNCTION if exists log_vehicle_request();
CREATE FUNCTION log_vehicle_request() RETURNS TRIGGER AS $log_vehicle_request$
	BEGIN
		NEW.request_times := date_trunc('second', localtimestamp) || NEW.request_times;
		RETURN NEW;
	END;
$log_vehicle_request$ LANGUAGE plpgsql;

CREATE TRIGGER log_vehicle_request 
	BEFORE INSERT OR UPDATE OF is_requested ON vehicles
	FOR EACH ROW WHEN (NEW.is_requested = TRUE)
	EXECUTE PROCEDURE log_vehicle_request();
