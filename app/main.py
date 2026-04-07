from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "mini-ai-resume-api is running"}