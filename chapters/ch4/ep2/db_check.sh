#!/bin/bash
docker exec mariadb mysql -D dsadeb_flights -u root -pmysql -e "select * from routes limit 10" --table=TRUE
