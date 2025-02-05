from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

# MongoDB configuration
MONGO_URI = "mongodb+srv://mongodbacc:mongodbacc@cluster0.r55es.mongodb.net/"
DATABASE_NAME = "db_quickbites"

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client[DATABASE_NAME]
    app.state.db = db  # Attach the database to app.state
    print("Connected to MongoDB")
    yield
    # Shutdown logic
    await mongo_client.close()
    print("MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class District(BaseModel):
    name :str

class City(BaseModel):
    name : str
    district_id : str 

class Place(BaseModel):
    name : str
    city_id : str

class Subcategory(BaseModel):
    name : str
    category_id : str

class Category(BaseModel):
    name : str
#user
class User(BaseModel):
    name : str
    email : str
    password : str

class Login(BaseModel):
    email : str
    password : str

@app.post('/signIn')
async def create_user(user : User):
    user_data = user.model_dump()
    result = await app.state.db["user"].insert_one(user_data)
    return { 'id' : str(result.inserted_id), 'message' : 'user created successfully'}

@app.post('/login')
async def read_user(user: Login):
    result = await app.state.db["user"].find_one({"email": user.email, "password": user.password})
    if result:
        return { 'id': str(result['_id']), 'message': 'login successful'}
    else:
        return { 'message': 'Invalid credentials' }

@app.post('/district')
async def create_district(district : District):
    district_data = district.model_dump()
    result = await app.state.db["district"].insert_one(district_data)
    return { "id" : str(result.inserted_id), "message" : "district created successfully"}


@app.get("/district")
async def read_district():
    cursor = app.state.db["district"].find()
    districtData = await cursor.to_list(length=None)  # Convert cursor to list
    for district in districtData:
        district["_id"] = str(district["_id"])
    if not districtData:
        raise HTTPException(status_code=404, detail="Item not found")
    return districtData



# Example route to get an item by ID
@app.get("/district/{district_id}")
async def read_item(district_id: str):
    district = await app.state.db["district"].find_one({"_id": ObjectId(district_id)})
    if not district:
        raise HTTPException(status_code=404, detail="Item not found")
    district["_id"] = str(district["_id"])  # Convert ObjectId to string for response
    return district




@app.post('/place')
async def create_place(place : Place):
    place_data = place.model_dump()
    result = await app.state.db["place"].insert_one(place_data)
    return { "id" : str(result.inserted_id), "message" : "place inserted successfully"}

@app.get("/city/{district_id}")
async def read_city(district_id: str):
    cursor = app.state.db["city"].find({"district_id": district_id})   
    cityData = await cursor.to_list(length=None)
    for city in cityData:
        city["_id"] = str(city["_id"])
    if not city:
        raise HTTPException(status_code=404, detail="Item not found")
    return cityData

@app.post('/city')
async def create_place(city : City):
    city_data = city.model_dump()
    result = await app.state.db["city"].insert_one(city_data)
    return { "id" : str(result.inserted_id), "message" : "city inserted successfully"}

@app.post('/category')
async def create_category(categroy : Category):
    categroy_data = categroy.model_dump()
    result = await app.state.db['category'].insert_one(categroy_data)
    return { "id" : str(result.inserted_id), "message" : "category inserted successfully"}



@app.post("/sub")
async def create_subcategory(sub : Subcategory):
    sub_data = sub.model_dump()
    result = await app.state.db["Subcategory"].insert_one(sub_data)
    return {"id" : str(result.inserted_id), "message" : "subcategory inserted successfully"}
