select service_providers.business_name, service_providers.business_description, service_providers.phone_num
FROM service_providers, provides_services_for, buildings, entrants, of_a
WHERE service_providers.business_id = provides_services_for.business_id and
	  provides_services_for.building_id = buildings.building_id and
	  buildings.building_id = of_a.building_id and of_a.entrant_id = entrants.entrant_id and
	  entrants.fname = 'Tania' and
	  to_tsvector(service_providers.business_description_long) @@ to_tsquery('clean');

SELECT vehicles.state, vehicles.plate_num, vehicles.request_times[1] as time_requested
FROM vehicles, buildings
WHERE vehicles.is_requested = True and vehicles.building_id = buildings.building_id and buildings.building_name = 'Atrium'
ORDER BY time_requested asc;
