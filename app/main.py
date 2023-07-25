from fastapi import Cookie, FastAPI, Form, Request, Response, templating, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import PurchasesRepository
from .users_repository import User, UsersRepository
from jose import jwt
from typing import List
import json

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()

def create_jwt(user_id: int) -> str:
    body = {"user_id": user_id}
    token = jwt.encode(body, "qwe", algorithm="HS256")
    return token

def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "qwe")
    return data["user_id"]

def hash_jwt(password: str):
    data = {"password": password}
    hashed_password = jwt.encode(data, "qwe", algorithm="HS256")
    return hashed_password


@app.get("/signup")
def signup():
    return users_repository

@app.post("/signup")
def post_signup(email: str=Form(), 
    name: str=Form(), 
    password: str=Form()
):
    hashed_password = hash_jwt(password)
    user = User(email=email, full_name=name, hashed_password=hashed_password)
    users_repository.save(user)
    return Response()

@app.post("/login")
def post_login(request: Request, 
    response: Response,
    email: str=Form(), 
    password: str=Form(),
):
    user = users_repository.get_by_email(email)
    if not user:
         raise HTTPException(status_code=400, detail="Incorrect username or password")
    hashed_password = hash_jwt(password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = create_jwt(user.id)
    return {"access_token": token, "type": "bearer"}

@app.get("/profile")
def get_profile(token: str = Cookie(), str=Depends(oauth2_scheme)):
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(user_id)
    if not users_repository.get_by_id(user_id["user_id"]):
        raise HTTPException(status_code=404, detail="Not Found")
    return {"email": user.email, "full_name": user.full_name, "id": user.id}


@app.get("/flowers")
def get_flowers(token: str=Depends(oauth2_scheme)):
    flowers = flowers_repository.get_all()
    return flowers

@app.post("/flowers")
def post_flowers(flower: Flower, token: str=Depends(oauth2_scheme)):
    id = flowers_repository.save(flower)
    return {"flower_id": id}


def get_cart_items(request: Request):
    cart_items = request.cookies.get("cart_items")
    if cart_items:
        cart_items = json.loads(cart_items)
    else:
        cart_items = []
    return cart_items


@app.post("/cart/items")
def post_cart_items(
    flower_id: int=Form(), 
    cart: str=Cookie(default="[]"), 
    token: str=Depends(oauth2_scheme)
):
    response = Response()
    cart_json = json.loads(cart)
    if 0 < flower_id and flower_id <= len(flowers_repository.get_all()):
        cart_json.append(flower_id)
        new_cart = json.dumps(cart_json)
        response.set_cookie("cart", new_cart)
    return response


@app.get("/cart/items")
def get_cart_items(cart: str=Cookie(default=None), token: str=Depends(oauth2_scheme)):
    response = []
    if cart == None:
        return Response("Cart is empty", media_type="text/plain")
    cart_json = json.loads(cart)
    flowers = flowers_repository.get_list_flowers(cart_json)
    total_cost = 0
    for flower in flowers:
        total_cost += flower.cost
        response.append({"flower_id": flower.id, "name": flower.name, "cost": flower.cost})
    response.append({"total_cost": total_cost})
    return response
