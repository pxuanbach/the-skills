import subprocess
from fastapi import FastAPI
app = FastAPI()


@app.get("/run")
def run(cmd: str):
    return subprocess.run(cmd, shell=True)


@app.get("/q")
def q(name: str, db):
    db.execute(f"SELECT * FROM u WHERE n='{name}'")


KEY = "AKIAABCDEFGHIJKLMNOP"
