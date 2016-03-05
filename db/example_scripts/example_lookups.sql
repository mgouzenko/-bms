-- Find all cars from the building called 'Buckingham Tower' that have been
-- requested by their driver. Also find the details of each car's driver. This
-- is a lookup that a valet coordinator can use to check which cars need to be
-- brought out from the garage. It would allow the coordinator to give the car
-- to the correct person.
SELECT entrants.fname, entrants.lname, vehicles.make,
	   vehicles.model, vehicles.plate_num, vehicles.state
FROM vehicles, drives, entrants, buildings
WHERE (
	vehicles.is_requested = true AND
	vehicles.plate_num = drives.plate_num AND
	vehicles.state = drives.state AND
	entrants.entrant_id = drives.entrant_id AND
	buildings.building_id = vehicles.building_id AND
	buildings.building_name = 'The Buckingham Tower');

-- Find out how many cars are parked at each building using grouping and the
-- aggregate COUNT. Order the output so that the buildings with the most parked
-- cars are at the top of the list.
SELECT buildings.building_name, COUNT(*)
FROM buildings, vehicles
WHERE buildings.building_id = vehicles.building_id
GROUP BY buildings.building_name
ORDER BY COUNT(*) DESC;

-- Find out where the resident Jessica Young lives. If there are multiple
-- Jessica Youngs, this query will give the address of every one of them in
-- separate row.
SELECT buildings.building_name, buildings.street_address, unit_entrants.unit_id,
	   buildings.city, buildings.state, buildings.zip_code
FROM entrants, unit_entrants, residents, buildings
WHERE (
	entrants.fname = 'Jessica' AND
	entrants.lname = 'Young' AND
	entrants.entrant_id = residents.entrant_id AND
	entrants.entrant_id = unit_entrants.entrant_id AND
	unit_entrants.building_id = buildings.building_id);
