from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.exercises import router as exercises_router
from routes.equipnments import router as equipnments_router
from routes.users import router as user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercises_router)
app.include_router(equipnments_router)
app.include_router(user_router)

@app.get("/")
async def root():
   return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)