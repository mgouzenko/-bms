DROP TABLE if exists Entrants;
CREATE TABLE Entrants (
	entrant_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (entrant_id));

DROP TABLE if exists Buildings;
CREATE TABLE Buildings (
	building_id INTEGER,
	name CHAR(40),
	PRIMARY KEY (building_id));

DROP TABLE if exists Of_A;
CREATE TABLE Of_A (
	building_id INTEGER,
	entrant_id INTEGER,
	PRIMARY KEY (building_id, entrant_id),
	FOREIGN KEY (entrant_id) REFERENCES Entrants,
	FOREIGN KEY (building_id) REFERENCES Buildings
);
