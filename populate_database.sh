#!/bin/bash

# entrants
psql -U mag2272 -h w4111a.eastus.cloudapp.azure.com proj1part2 \
	-c "copy entrants from STDIN with delimiter as ','" < ./db/example_data/entrants.csv

# admins
psql -U mag2272 -h w4111a.eastus.cloudapp.azure.com proj1part2 \
	-c "copy admins from STDIN with delimiter as ','" < ./db/example_data/admins.csv

# service_employees
psql -U mag2272 -h w4111a.eastus.cloudapp.azure.com proj1part2 \
	-c "copy service_employees from STDIN with delimiter as ','" < ./db/example_data/service_employees.csv

# buildings
psql -U mag2272 -h w4111a.eastus.cloudapp.azure.com proj1part2 \
	-c "copy buildings from STDIN with delimiter as ','" < ./db/example_data/buildings.csv

# service_providers
psql -U mag2272 -h w4111a.eastus.cloudapp.azure.com proj1part2 \
	-c "copy service_providers from STDIN with delimiter as ','" < ./db/example_data/service_providers.csv
