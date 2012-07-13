live:	
	m4 -D domain=www.placethings.com placethings/settings.py.m4 > placethings/settings.py
	m4 placethings/django.wsgi.m4 > placethings/django.wsgi
	apachectl graceful

development:
	m4 -D domain=placethings -D debug placethings/settings.py.m4 > placethings/settings.py
	m4 placethings/django.wsgi.m4 > placethings/django.wsgi
	sudo apache2ctl graceful
	
test:
	./placethings/manage.py test api

johntron:
	m4 -D domain=placethings.johntron.com -D debug placethings/settings.py.m4 > placethings/settings.py
	m4 placethings/django.wsgi.m4 > placethings/django.wsgi
	sudo apache2ctl graceful

dumpschema:
	mysqldump -u root -p placethings_dev --no-data > /www/placethings.com/www/schema.sql

trace:
	m4 -D debug placethings/django.wsgi.m4 > placethings/django.wsgi
	sudo apache2ctl stop
	sudo apache2ctl -X