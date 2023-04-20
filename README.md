# Seasoned Care

Chat bot

## Installation

1. Clone this repository to your local machine: `git clone git@github.com:jumasheff/seasoned_care.git && cd seasoned_care`
2. Create .env file: `cp .env_template .env`
3. Edit `.env`: paste your OPENAI_API_KEY (without quotation marks)
4. Run the following command to download and extract the database, create a virtual environment and install dependencies, run migrations, and load fixtures (I assume you have `curl`). It'll take ~3-4 minutes:

```shell
make build
```

5. Run the project:

```shell
make run
```

6. Go to localhost:8000/admin and login (username: admin password: admin123admin). Otherwise the chat won't work.
7. Go to localhost:8000/chat and have fun!

## Credits

This project is built using incredible framework called [LangChain](https://github.com/hwchase17/langchain)

Also, I used [MedQuaD](https://github.com/abachaa/MedQuAD) as a dataset.
To view the full list of tools, see requirements.
