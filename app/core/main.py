from fastapi import FastAPI
from app.endpoints import twilio_webhooks

app = FastAPI()
app.include_router(twilio_webhooks.router)