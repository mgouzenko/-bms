#!/bin/bash

./load_schema.sh
declare -a arr=("entrants" 					\
				"admins" 					\
				"service_employees"			\
				"buildings"					\
				"service_providers"			\
				"works_for"					\
				"administers"				\
				"parking_spots"				\
				"vehicles"					\
				"of_a"						\
				"provides_services_for"		\
				"drives"					\
				"units"						\
				"unit_entrants"				\
				"residents"					\
				"casual_entrants"			\
				"guests"					\
				"owns")

for table_name in "${arr[@]}"
do
	psql \
		-U mag2272 \
		-h w4111a.eastus.cloudapp.azure.com proj1part2 \
		-c "copy $table_name from STDIN with delimiter as ','" \
		< ./db/example_data/$table_name.csv
done
