from bson import ObjectId
from fastapi import FastAPI, HTTPException, File, UploadFile,Form
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os
import aiofiles
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext  # For password hashing


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

# MongoDB configuration
MONGO_URI = ""
DATABASE_NAME = ""

UPLOAD_DIR = "uploads"  # Directory to save uploaded files

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utility function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Utility function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



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


# Utility function to save the file
# async def save_file(file: UploadFile, upload_dir: str) -> str:
#     os.makedirs(upload_dir, exist_ok=True)
#     file_path = os.path.join(upload_dir, file.filename)
#     async with aiofiles.open(file_path, "wb") as out_file:
#         while content := await file.read(1024):
#             await out_file.write(content)
#     return file_path


async def save_file(file: UploadFile, upload_dir: str) -> str:
    login= print(photo)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        while True:
            content = await file.read(1024)
            if not content:  # Handle empty reads
                break
            await out_file.write(content)
    return file_path




app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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
    userData = await app.state.db["user"].find_one({"email": user.email, "password": user.password})
    resData = await app.state.db["restaurant"].find_one({"email": user.email, "password": user.password})
    resData = await app.state.db["restaurant"].find_one({"email": user.email, "password": user.password})
    resData = await app.state.db["restaurant"].find_one({"email": user.email, "password": user.password})

    if userData:
        return { 'id': str(userData['_id']), 'message': 'login successful','login':'User'}
    elif resData:
        return { 'id': str(resData['_id']), 'message': 'login successful','login':'Restaurant'}
    elif resData:
        return { 'id': str(resData['_id']), 'message': 'login successful','login':'Restaurant'}
    elif resData:
        return { 'id': str(resData['_id']), 'message': 'login successful','login':'Restaurant'}
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


# @app.post('/restaurantRegister')
# async def create_restaurant(restaurant : Restaurant):
#     restaurant_data = restaurant.model_dump()
#     result = await app.state.db["restaurant"].insert_one(restaurant_data)
#     return{'id' : str(result.inserted_id), 'message' : "restaurant created successfully"}

# class Restaurant(BaseModel):
#     name : str
#     email : str
#     password : str
#     address : str
#     photo: str



@app.post("/restaurantRegister/")
async def create_restaurant(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    address: str = Form(...),
    photo: UploadFile = File(...)
):
    try:
        # Save the file
        saved_filename = await save_file(photo, UPLOAD_DIR)
        file_url = f"http://127.0.0.1:8000/uploads/{photo.filename}"

        # Hash the password
        hashed_password = hash_password(password)
        # Insert data into MongoDB
        user_data = {"name": name,"address": address, "email": email, "password": hashed_password, "photo": file_url}
        result = await app.state.db["restaurant"].insert_one(user_data)
        return {
            "id": str(result.inserted_id),
            "message": "User created successfully",
            "file_path": file_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")