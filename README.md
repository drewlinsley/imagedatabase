# Create database for storing results
	a. sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common #Install posetgresql with online installer
	b. sudo -i -u postgres #goes into postgres default user
	c. psql postgres #enter the postgres interface
	d. create role imagedatabase WITH LOGIN superuser password 'serrelab'; #create the admin
	e. alter role imagedatabase superuser; #ensure we are sudo
	f. create database imagedatabase with owner imagedatabase; #create the database
	g. \q #quit
	h. psql imagedatabase -h 127.0.0.1 -d imagedatabase
