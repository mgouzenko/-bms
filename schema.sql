CREATE TABLE Entrants (
	entrant_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (entrant_id)
);

CREATE TABLE Admins ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

CREATE TABLE Residents ( --superclass is entrants
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

CREATE TABLE Casual_Entrants ( --superclass is entrants 
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

CREATE TABLE Guests ( --superclass is entrants 
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

CREATE TABLE Service_Employees ( --superclass is entrants 
	entrant_id INTEGER,
	PRIMARY KEY (entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants
);

CREATE TABLE Buildings (
	building_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (building_id)
);

CREATE TABLE Service_Providers (
	business_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (id)
);

CREATE TABLE Works_For (
	entrant_id INTEGER,
	business_id INTEGER,
	PRIMARY KEY (entrant_id, business_id),
	FOREIGN KEY (entrant_id) REFERENCES Service_Employees,
	FOREIGN KEY (business_id) REFERENCES Service_Providers
)

CREATE TABLE Administers (
	entrant_id INTEGER,
	building_id INTEGER,
	PRIMARY KEY (entrant_id, building_id),
	FOREIGN KEY (entrant_id) REFERENCES Admins,
	FOREIGN KEY (building_id) REFERENCES Buildings
)

CREATE TABLE Vehicles (
	state CHAR (2),
	plate_num CHAR(10),
	color CHAR(15),
	PRIMARY KEY (state, plate_num)
);

CREATE TABLE Of_A ( -- Entrant of a building
	building_id INTEGER,
	entrant_id INTEGER,
	PRIMARY KEY (building_id, entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants,
	FOREIGN KEY (building_id) REFERENCES Buildings
);

CREATE TABLE Provides_Services_For ( -- buildings that service providers provide)
	business_id INTEGER,
	building_id INTEGER,
	PRIMARY KEY (business_id, building_id),
	FOREIGN KEY (business_id) REFERENCES Service_Providers,
	FOREIGN KEY (building_id) REFERENCES Buildings
);

CREATE TABLE Drives (
	entrant_id INTEGER,
	state CHAR (2),
	plate_num CHAR(10),
	PRIMARY KEY (entrant_id, state, plate_num),
	FOREIGN KEY (entrant_id) REFERENCES Entrants,
	FOREIGN KEY (state, plate_num) REFERENCES Vehicles
);

CREATE TABLE Units_Within ( -- unit within a building
	unit_id CHAR(6),
	building_id INTEGER NOT NULL,
	PRIMARY KEY (unit_id, building_id),
	FOREIGN KEY (building_id) REFERENCES Buildings, ON DELETE CASCADE
);

CREATE TABLE Parking_Spots_Within ( -- parking spots within a building
	spot_number INTEGER,
	building_id INTEGER NOT NULL,
	PRIMARY KEY (spot_number, building_id),
	FOREIGN KEY (building_id) REFERENCES Buildings, ON DELETE CASCADE
);

CREATE TABLE Enters ( -- The unit which a particular entrant is entering (or a resident of, or guest of)
	entrant_id INTEGER,
	unit_id CHAR(6),
	building_id INTEGER,
	PRIMARY KEY (entrant_id, unit_id, building_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants,
	FOREIGN KEY (unit_id, building_id) REFERENCES Units_Within
)

CREATE TABLE Owns ( -- parking spot owned by a unit
	unit_id CHAR(6),
	spot_number INTEGER,
	building_id INTEGER,
	PRIMARY KEY (unit_id, building_id, spot_number),
	FOREIGN KEY (unit_id, building_id) REFERENCES Units_Within,
	FOREIGN KEY (spot_number, building_id) REFERENCES Parking_Spots_Within,
);

CREATE TABLE Occupies ( -- vehicle occupying a parking spot
	spot_number INTEGER,
	building_id INTEGER,
	state CHAR(2),
	plate_num CHAR(10),
	PRIMARY KEY (spot_number, building_id, state, plate_num),
	FOREIGN KEY (unit_id, building_id) REFERENCES Units_Within,
	FOREIGN KEY (spot_number, building_id) REFERENCES Parking_Spots_Within
)