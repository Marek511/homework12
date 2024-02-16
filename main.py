from fastapi import FastAPI
import uvicorn
import router_endpoints

app = FastAPI()

app.include_router(router_endpoints.router, prefix="/contacts")


@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)