References: 








GET:(from url)
http://127.0.0.1:8000/text/?start-date=2016-07-01&end-data=2016-07-07&submitchange=SubmitClick#

POST(from message, more secure to change data)
http://127.0.0.1:8000/text/?start-date=2016-07-01&end-data=2016-07-07&submitchange=SubmitClick






##Create new db:
1. delete db.sqlite3
2. python manage.py makemigrations
3. python manage.py migrate --run-syncdb
4. python manage.py migrate
5. python manage.py runserver






##TimeZone:
raise AmbiguousTimeError(dt)
pytz.exceptions.AmbiguousTimeError: 2016-10-30 02:47:09
==>doc_no: 4995
==>text: temperature down 5°C -&gt; 4°C
==> is_dst=None





