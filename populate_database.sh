#!/bin/bash

psql -U mag2272 -h w4111a.eastus.cloudapp.azure.com proj1part2 \
	-c "copy entrants from STDIN with delimiter as ','" < ./db/example_data/entrants.csv
