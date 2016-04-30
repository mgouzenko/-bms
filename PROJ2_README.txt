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

SELECT service_providers.business_name, service_providers.business_description, service_providers.phone_num
FROM service_providers, provides_services_for, buildings, entrants, of_a
WHERE service_providers.business_id = provides_services_for.business_id and
	  provides_services_for.building_id = buildings.building_id and
	  buildings.building_id = of_a.building_id and of_a.entrant_id = entrants.entrant_id
	  and entrants.fname = 'Tania' and entrants.lname = 'Gouzenko' and
	  to_tsvector(service_providers.business_description_long) @@ to_tsquery('clean');

This query joins service providers with the buildings the service, and looks
for tuples where the building id is the same as the one Tania Gouzenko lives
in. The result of this query is:

     business_name      |                        business_description                         | phone_num
------------------------+---------------------------------------------------------------------+------------
 Bob’s Cleaning         | General cleaning and housekeeping                                   | 2040204040
 Air Conditioners R Us  | Repair , cleaning and installation of air conditioners and heaters. | 4785878596
 Lisa’s Carpet Cleaners | Deep carpet steaming.                                               | 4325423544
(3 rows)

Now, Tania can comfortably pick up the phone and call any one of those
services, depending on what needs she has.

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

SELECT vehicles.state, vehicles.plate_num, vehicles.request_times[1] as time_requested
FROM vehicles, buildings
WHERE vehicles.is_requested = True and
	  vehicles.building_id = buildings.building_id and
	  buildings.building_name = 'Atrium'
ORDER BY time_requested asc;

The result of the query is a list of cars ordered with the most urgent
requests at the top of the list:

 state | plate_num |   time_requested
-------+-----------+---------------------
 NY    | 36275     | 2016-04-05 09:15:23
 NY    | 62581     | 2016-04-05 09:20:23
(2 rows)

Of course, this functionality could be implemented by maintaining a single
timestamp for the last request time. But, due to legal issues, the valet
administrators must keep a log book of all the times they retreived a given car.
This is actually a requirement in a building whose management we spoke to; if
there are ever any accusations of damage, the management can look at the
valet's handwritten logs and see what times the car in question was retrieved.
