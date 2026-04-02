# main.py — The entrypoint of your application.
#
# This file does THREE things:
# 1. Creates the FastAPI app instance
# 2. Includes routers (each router is a group of related endpoints)
# 3. Runs the server when you do `python main.py`
#
# Keep this file thin — business logic belongs in services/, not here.

import uvicorn
from fastapi import FastAPI
from app.routes.chat import router as chat_router

app = FastAPI(
    title="LLM Chatbot API",
    description="A minimal chatbot API powered by OpenAI",
)

# Include the chat router — this adds the POST /chat endpoint
app.include_router(chat_router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)