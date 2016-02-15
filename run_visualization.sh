#!/bin/bash
java -jar ./third_party/schemaSpy_5.0.0.jar -t pgsql -host 127.0.0.1:5432 -db bms -u mgouzenko -s public -dp ./third_party/postgresql-9.4.1207.jar -o ./visualization
