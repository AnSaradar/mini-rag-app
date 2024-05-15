from fastapi import FastAPI

app = FastAPI()

@app.get("/welcome")
def welcome():
    return {
        "Message" : "WELCOME TO FAST API "
    }