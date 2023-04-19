# Seasoned Care

Chat bot

## Installation

1. Clone this repository to your local machine: `git clone git@github.com:jumasheff/seasoned_care.git`
2. `mv .env_template` to `.env`
3. Edit `.env`: paste your OPENAI_API_KEY
4. Run the following command to download and extract the database, create a virtual environment and install dependencies:

```shell
make build
```

5. Run the project:

```shell
make run
```

6. Go to localhost:8000/admin and login. Otherwise the chat won't work
7. Go to localhost:8000/chat and have fun!
