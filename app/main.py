from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
