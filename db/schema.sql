DROP TABLE if exists Entrants;
CREATE TABLE Entrants (
	entrant_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (entrant_id)
);

DROP TABLE if exists Admins;
CREATE TABLE Admins ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

DROP TABLE if exists Residents;
CREATE TABLE Residents ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

DROP TABLE if exists Casual_Entrants;
CREATE TABLE Casual_Entrants ( --superclass is entrants 
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

DROP TABLE if exists Guests;
CREATE TABLE Guests ( --superclass is entrants 
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

DROP TABLE if exists Service_Employees;
CREATE TABLE Service_Employees ( --superclass is entrants 
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

DROP TABLE if exists Buildings;
CREATE TABLE Buildings (
	building_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (building_id)
);

DROP TABLE if exists Service_Providers;
CREATE TABLE Service_Providers (
	business_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (id)
);

DROP TABLE if exists Works_For;
CREATE TABLE Works_For (
	entrant_id INTEGER,
	business_id INTEGER,
	PRIMARY KEY (entrant_id, business_id),
	FOREIGN KEY (entrant_id) REFERENCES Service_Employees,
	FOREIGN KEY (business_id) REFERENCES Service_Providers
)

DROP TABLE if exists Administers;
CREATE TABLE Administers (
	entrant_id INTEGER,
	building_id INTEGER,
	PRIMARY KEY (entrant_id, building_id),
	FOREIGN KEY (entrant_id) REFERENCES Admins,
	FOREIGN KEY (building_id) REFERENCES Buildings
)

DROP TABLE if exists Vehicles;
CREATE TABLE Vehicles (
	state CHAR (2),
	plate_num CHAR(10),
	color CHAR(15),
	PRIMARY KEY (state, plate_num)
);

DROP TABLE if exists Of_A;
CREATE TABLE Of_A ( -- Entrant of a building
	building_id INTEGER,
	entrant_id INTEGER,
	PRIMARY KEY (building_id, entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants,
	FOREIGN KEY (building_id) REFERENCES Buildings
);

DROP TABLE if exists Provides_Services_For;
CREATE TABLE Provides_Services_For ( -- buildings that service providers provide)
	business_id INTEGER,
	building_id INTEGER,
	PRIMARY KEY (business_id, building_id),
	FOREIGN KEY (business_id) REFERENCES Service_Providers,
	FOREIGN KEY (building_id) REFERENCES Buildings
);

DROP TABLE if exists Drives;
CREATE TABLE Drives (
	entrant_id INTEGER,
	state CHAR (2),
	plate_num CHAR(10),
	PRIMARY KEY (entrant_id, state, plate_num),
	FOREIGN KEY (entrant_id) REFERENCES Entrants,
	FOREIGN KEY (state, plate_num) REFERENCES Vehicles
);

DROP TABLE if exists Units_Within;
CREATE TABLE Units_Within ( -- unit within a building
	unit_id CHAR(6),
	building_id INTEGER NOT NULL,
	PRIMARY KEY (unit_id, building_id),
	FOREIGN KEY (building_id) REFERENCES Buildings, ON DELETE CASCADE
);

DROP TABLE if exists Parking_Spots_Within;
CREATE TABLE Parking_Spots_Within ( -- parking spots within a building
	spot_number INTEGER,
	building_id INTEGER NOT NULL,
	PRIMARY KEY (spot_number, building_id),
	FOREIGN KEY (building_id) REFERENCES Buildings, ON DELETE CASCADE
);

DROP TABLE if exists Enters;
CREATE TABLE Enters ( -- The unit which a particular entrant is entering (or a resident of, or guest of)
	entrant_id INTEGER,
	unit_id CHAR(6),
	building_id INTEGER,
	PRIMARY KEY (entrant_id, unit_id, building_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants,
	FOREIGN KEY (unit_id, building_id) REFERENCES Units_Within
)

DROP TABLE if exists Owns;
CREATE TABLE Owns ( -- parking spot owned by a unit
	unit_id CHAR(6),
	spot_number INTEGER,
	building_id INTEGER,
	PRIMARY KEY (unit_id, building_id, spot_number),
	FOREIGN KEY (unit_id, building_id) REFERENCES Units_Within,
	FOREIGN KEY (spot_number, building_id) REFERENCES Parking_Spots_Within,
);

DROP TABLE if exists Occupies;
CREATE TABLE Occupies ( -- vehicle occupying a parking spot
	spot_number INTEGER,
	building_id INTEGER,
	state CHAR(2),
	plate_num CHAR(10),
	PRIMARY KEY (spot_number, building_id, state, plate_num),
	FOREIGN KEY (unit_id, building_id) REFERENCES Units_Within,
	FOREIGN KEY (spot_number, building_id) REFERENCES Parking_Spots_Within
)