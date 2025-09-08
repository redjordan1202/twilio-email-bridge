# Chiron Relay
#### A serverless bidirectional communication relay allowing for receiving and send SMS messages via email and Discord

## 🚀 Key Features 
- __Secure Webhook Ingestion:__ Validates incoming requests from Twilio using Twilio's recommend `HMAC-SHA1` signature validation process, ensuring all processed requests are valid and secure
- __Async Task Processing:__ All validation and processing are handled as FastAPI BackgroundTasks to provide a fast and responsive API experience
- __Structured JSON Logging:__ All logging is done using structured JSON logging to provide clean, human-readable logging free of any personal information
- __SMS Forwarding via Gmail:__ Inbound SMS messages are forwarded to email via the Gmail API and domain-wide delegation


## 🛠️ Tech Stack
- __Back End:__ Python 3.11, FastAPI
- __Cloud Platforms:__ Google Cloud Functions
- __APIS:__ Twilio Programmable SMS, Gmail API
- __Testing:__ Pytest, unittest

## ⚙️ Setup 

### Docker Deployment
This section assumes you already have docker and docker compose working on your system

1. Clone the repository:
```bash
git clone https://github.com/redjordan1202/twilio-email-bridge.git
cd twilio-email-bridge
```

2. build the docker image
```bash
docker build -t chiron-relay
```

3. Make a `.env` file from provided `.env.example`
```bash
cp .env.example .env
```

4. Edit the .env file with your twilio and google secrets. More information can found in the setup guides below


5. Create a `secrets` directory in the project root
```bash
mkdir secrets
```

 
6. Copy your google service account's account.json to the new `secrets` directory.
More info can be found in the google set up guide below


7. Use docker compose to start the container
```bash
# To see logs in the console output
docker compose up
# To run detached
docker compose up --detach
```

### Local Deployment (Without Docker)

1. Clone the repository:
```bash
git clone https://github.com/redjordan1202/twilio-email-bridge.git
cd twilio-email-bridge
```


2. Create and Activate a Python Virtual Environment
```bash
python -m venv venv
# For Linux/MacOS
source venv/bin/activate
# For Windows (Powershell)
.\venv\Scripts\Activate.ps1
```


3. Install Dependencies
```bash
pip install -r requirements.txt
```


4. Make a `.env` file from provided `.env.example`
```bash
cp .env.example .env
```


5. Edit the .env file with your twilio and google secrets
	
	**NOTE** for local deployments you must set `GOOGLE_APPLICATION_CREDENTIALS` 
	to the absolute path of your account keyfile.


6. Launch the app
```bash
uvicorn app.core.main:app --host 127.0.0.1 --port 8080 --reload
# You may also run main.py in the project root.
# This however will give you less control over the uvicorn server setup
python -m main.py
```



## External services set up
This program relies heavily on Twilio and Google services to provide functionality.
The below guides will walk you through the process of setting up both for this project. 

Twilio Setup Guide (In Development)
Google Cloud Services Setup Guide (In Development)