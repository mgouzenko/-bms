Mitchell Gouzenko - mag2272
Adam Chelminski - apc2142
Project 2

Postgresql account: mag2272

First Item: Text Attribute and Search
********************************************************************************
Recall that in our service_providers relation, we store information about the
businesses that provide services for buildings in our system. Previously, each
business had a VARCHAR attribute called business_description. This was a short
description of the services the business offers.

In this part, we decided to add a new text attribute to the business relation
called "business_description_long". This is a field in which businesses can
specify a longer and more detailed business description, in which they might
enumerated the variety of services they can perform. The purpose of such
an attribute is to permit text search over business descriptions. For
instance, suppose Tania Gouzenko is searching for a cleaning service
for her unit. She can do a text search on the word 'clean' as follows:

-- Meaningful Query #1 --
SELECT service_providers.business_name, service_providers.business_description, service_providers.phone_num
FROM service_providers, provides_services_for, buildings, entrants, of_a
WHERE service_providers.business_id = provides_services_for.business_id and
	  provides_services_for.building_id = buildings.building_id and
	  buildings.building_id = of_a.building_id and of_a.entrant_id = entrants.entrant_id
	  and entrants.fname = 'Tania' and entrants.lname = 'Gouzenko' and
	  to_tsvector(service_providers.business_description_long) @@ to_tsquery('clean');

This query joins service providers with the buildings they provide services
for, and looks only for tuples where the building id is the same as the one Tania
Gouzenko lives in. The result of this query is:

     business_name      |                        business_description                         | phone_num
------------------------+---------------------------------------------------------------------+------------
 Bob’s Cleaning         | General cleaning and housekeeping                                   | 2040204040
 Air Conditioners R Us  | Repair , cleaning and installation of air conditioners and heaters. | 4785878596
 Lisa’s Carpet Cleaners | Deep carpet steaming.                                               | 4325423544
(3 rows)

Now, Tania can comfortably pick up the phone and call any one of those
services, depending on what needs she has. When she does so, she knows that
the businesses in the result already have a professional relationship with the
building she lives in.

Second Item: Timestamp Arrays for Car Requests
********************************************************************************
Suppose the valet administrators have multiple requests for cars. Which car
should they deliver first? Intuitively, the valet drivers should prioritize
the earliest-requested cars. This was not a feature we built into our
original DBMS. To remedy the problem, we added an attribute to vehicles called
"request_times", which is an array of timestamps corresponding to when the car
was requested. The idea is that whenever a resident requests a car, the time
of the request is appended to the head of the timestamp array.

Now, suppose the valet for Atrium has a series of vehicle requests queued up.
To see which vehicle they should retrieve first, the valet administrator can
run the following query:

-- Meaningful Query #2 --
SELECT vehicles.state, vehicles.plate_num, vehicles.request_times[1] as time_requested
FROM vehicles, buildings
WHERE vehicles.is_requested = True and
	  vehicles.building_id = buildings.building_id and
	  buildings.building_name = 'Atrium'
ORDER BY time_requested asc;

The result of the query is a list of cars ordered with the most urgent requests 
at the top of the list. The first element of the request_times array is used so 
that the most recent request time for a particular car is used:

 state | plate_num |   time_requested    
-------+-----------+---------------------
 NY    | 36275     | 2016-05-01 01:02:27
 NY    | 62581     | 2016-05-01 01:07:12

Of course, this functionality could be implemented by maintaining a single
timestamp for the last request time. However, due to legal issues, the valet
administrators must keep a log book of all the times they retreived a given 
car. This is actually a requirement in a building whose management we spoke 
to; if there are ever any accusations of damage, the management can look at the
valet's handwritten logs and see what times the car in question was retrieved.
That way, they know what times to inspect in surveillance camera footage.

The following query lists all the request times for a particular vehicle in a 
particular building:

-- Meaningful Query #3 --
SELECT unnest(vehicles.request_times) as request_time
FROM vehicles, buildings
WHERE vehicles.state = 'NY' and
	  vehicles.plate_num = '62581' and
	  buildings.building_name = 'Atrium' and
	  vehicles.building_id = buildings.building_id
ORDER BY request_time asc;

The result of the query is a list of every time that the car from 'NY' with 
license plate '62581' was requested at the building 'Atrium', in ascending
order:
    request_time     
---------------------
 2016-04-02 09:30:00
 2016-04-03 09:18:24
 2016-04-05 09:20:23
 2016-05-01 01:02:27
(4 rows)

This list could be useful if, for legal reasons, someone needs to go back and 
check all the times that a particular car was requested.

Third Item: Trigger that updates request_times of a vehicle when requested
********************************************************************************
Expanding upon the previous item, it would be useful if the request_times 
array was automatically updated whenever a car is requested. To accomplish this
without implementing it at the application level, we added a trigger that would
automatically prepend the current time to the request_times array of a vehicle 
when its is_requested attribute is set to TRUE.

Suppose the car from MA with the license plate 51613 is requested in the
building with 'id' 12346 with the following update command:

UPDATE vehicles
SET is_requested = TRUE
WHERE vehicles.state = 'MA' and
	  vehicles.plate_num = '51613' and
	  vehicles.building_id = 12346;

This update command is an event that causes the trigger to be executed. As a
result, the current time will be added to the beginning of the 
request_times array of this particular vehicle.

We can check the times that this vehicle was requested with the following 
query

SELECT unnest(vehicles.request_times) as request_time
FROM vehicles
WHERE vehicles.state = 'MA' and
	  vehicles.plate_num = '51613' and
	  vehicles.building_id = 12346;

Before the update command is issued, the result of this query may look
like this:

request_time     
---------------------
 2016-04-03 12:22:22
 2016-04-03 06:08:01
(2 rows)

If the update command is issued at around 01:03 on May 1st, 2016 the result of
the query would look like this:

    request_time     
---------------------
 2016-05-01 01:03:17
 2016-04-03 12:22:22
 2016-04-03 06:08:01
(3 rows)

Because this time is added to the beginning of the array instead of the end, 
the query discussed in the second item (the query that lists the request times
of vehicles in a particular building) will always refer to the most recent
request time of any given vehicle, rather than a historical request time.
