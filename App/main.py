
from re import template
from fastapi.responses import HTMLResponse, RedirectResponse
from pymongo import MongoClient
from datetime import datetime

from typing import Optional
from click import File

from fastapi import Depends, FastAPI,Request,Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
import pprint


printer = pprint.PrettyPrinter()

client = MongoClient("mongodb+srv://lokesh:123@cluster0.lyeh3dg.mongodb.net/?retryWrites=true&w=majority")
insta_db = client.instagram
user_collection = insta_db.user_details
post_collection = insta_db.post_details


app = FastAPI()
logged_in_user = ""
templates = Jinja2Templates(directory= 'templates')
app.mount('/static',StaticFiles(directory= "static"),name = "static")


@app.get('/',response_class=HTMLResponse)
async def get_registration(request:Request):
    return templates.TemplateResponse("signup.html",{'request':request})




@app.post('/signup',response_class=HTMLResponse)
async def post_registration(request:Request,
                    username:str = Form(...),
                    password:str = Form(...),
                    email:str = Form(...),
                    firstname:str = Form(...),
                    lastname:str = Form(...)):
    print("post method called")
    print(username,password,email,firstname,lastname)
    person ={'username':username,'password':password,'email':email,'firstname':firstname,'lastname':lastname}
    user_collection.insert_one(person)
    return templates.TemplateResponse("login.html",{'request':request})


@app.get('/login',response_class=HTMLResponse)
async def post_registration(request:Request):
    print("getlogin")
    
    return templates.TemplateResponse("login.html",{'request':request})


@app.post('/login',response_class=HTMLResponse)
async def login_page(request:Request,username:str = Form(...),password:str = Form(...)):
    print("post login")
    print(username)
    print(password)

    name = user_collection.find_one({'username':username,'password':password})
    if name:
        print("loggedin")
        global logged_in_user
        logged_in_user = username
        return RedirectResponse("/home")
    else:
        print("No login")
        return RedirectResponse('/login')





@app.get('/home', response_class=HTMLResponse)
async def home_page(request: Request):

    people = user_collection.find()
    posts_details = post_collection.find()


    posts_dic={}
    # for pos in posts_details:
    #     posts_dic[pos['username']] ={
    #         'caption':pos['caption'],
    #         'description':pos['description'],
    #         'likes':len(pos['likes']),
    #     }

    return templates.TemplateResponse("home.html", {'request': request, 'user': logged_in_user,'posts':posts_dic})









@app.get('/addpost',response_class=HTMLResponse)
async def home_page(request:Request):
    return templates.TemplateResponse("create.html",{'request':request,'user':logged_in_user})







@app.post('/add_image',response_class = HTMLResponse)
async def add_image(request:Request,
                    caption:str = Form(...),
                    description:str = Form(...),
                    image_database: UploadFile = File(...)):
    
    global logged_in_user
    post = {'username':logged_in_user,
            'caption':caption,
            'description':description,
            'image_filename': image_database.filename,
            'likes':[],
            'created_at': datetime.now()
        }
    
    post_collection.insert_one(post)


    return templates.TemplateResponse('home.html',{'request':request,'user':logged_in_user})


@app.post('/add_video',response_class = HTMLResponse)
async def add_video(request:Request,
                    caption:str = Form(...),
                    description:str = Form(...),
                    video_database: UploadFile = File(...)):
    global logged_in_user
    post = {'username':logged_in_user,
            'caption':caption,
            'description':description,
            'video_filename': video_database.filename,
            'likes':[],
            'created_at': datetime.now()
        }
    # print(post)
    post_collection.insert_one(post)
    return templates.TemplateResponse('home.html',{'request':request,'user':logged_in_user})