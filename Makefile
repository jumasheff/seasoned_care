S3_URL := "https://aktan-tests.s3.eu-central-1.amazonaws.com/vector_db.zip"
ZIP_FILE := vector_db.zip

.PHONY: build

build:
	curl -o $(ZIP_FILE) $(S3_URL)
	unzip $(ZIP_FILE) -d vector_db
	python3 -m venv env
	bash -c "source env/bin/activate"
	pip install -r requirements.txt
