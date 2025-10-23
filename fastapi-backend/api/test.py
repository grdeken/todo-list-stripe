"""Simple test handler for Vercel."""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
