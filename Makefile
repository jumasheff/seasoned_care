S3_URL := "https://aktan-tests.s3.eu-central-1.amazonaws.com/vector_db.zip"
ZIP_FILE := vector_db.zip

.PHONY: build

build:
	curl -o $(ZIP_FILE) $(S3_URL)
	unzip $(ZIP_FILE) -d .
	test -d env || python3 -m venv env
	. env/bin/activate && pip install -r requirements.txt
	. env/bin/activate && cd webapp && ./manage.py migrate
	. env/bin/activate && cd webapp && ./manage.py createsuperuser --username admin

run:
	. env/bin/activate && cd webapp && ./manage.py runserver