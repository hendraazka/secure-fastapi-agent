from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"

def debug_list_files(user_input: str):
    import subprocess
    subprocess.call("ls " + user_input, shell=True)  # sengaja: shell injection buat test Bandit