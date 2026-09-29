import asyncio

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import Runner

from agent import mail_agent


app = FastAPI(title="Mail Agent API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Production me specific origin use karna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="No question provided."
        )

    try:
        result = await Runner.run(mail_agent, question)
        return {
            "answer": result.final_output
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }