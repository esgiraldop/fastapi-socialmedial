from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hello world"}

print("Application running in port 8000")
