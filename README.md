# Chiron Relay
#### A serverless bi-directional communication relay allowing for receiving and send SMS messages via email and Discord

## 🚀 Key Features
- __Secure Webhook Ingestion:__ Validates incoming requests from Twilio using Twilio's recommend `HMAC-SHA1` signature validation process, ensuring all processed requests are valid and secure
- __Async Task Processing:__ All validation and processing are handled as FastAPI BackgroundTasks to provide a fast and responsive API experience
- __Structured JSON Logging:__ All logging is done using structured JSON logging to provide clean, human readable logging free of any personal information


## 🛠️ Tech Stack
- __Back End:__ Python 3.11, FastAPI
- __Cloud Platforms:__ Google Cloud Functions
- __APIS:__ Twilio Programmable SMS
- __Testing:__ Pytest, unittest

## ⚙️ Setup 

For local deployments and testing please follow the below steps.
listed instructions are for use with bash or similar terminals

1. Clone the repository:
	```bash
	git clone https://github.com/redjordan1202/twilio-email-bridge.git
	```
2. Create and activate virtual python environment
	```bash
	python -m venv .venv
	source .venv/bin/activate
	```
3. Install dependancies
	```bash
	pip install -r requirements.txt
	```
4. Make a `.env` file from provided `.env.example`
```bash
cp .env.examples .env
```
5. Use your favorite text editor to change example Account SID and Auth Token to match those listed on your Twilio account. More info can be found in the Twilio Setup Guide linked below.
6. Run development server for testing and setup
	```bash
	uvicorn app.core.main:app --reload
	```


## External services set up
This program relies heavily on Twilio and Google services to provide functionality.
The below guides will walk you through the process of setting up both for this project. 

Twilio Setup Guide (In Development)
Google Cloud Services Setup Guide (In Development)