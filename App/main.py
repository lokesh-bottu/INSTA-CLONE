
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
def get_registration(request:Request):
    return templates.TemplateResponse("signup.html",{'request':request})



@app.post('/signup',response_class=HTMLResponse)
def post_registration(request:Request,
                    username:str = Form(...),
                    password:str = Form(...),
                    email:str = Form(...),
                    firstname:str = Form(...),
                    lastname:str = Form(...),
                    image_database: UploadFile = File(...)):
   

    print(username,password,email,firstname,lastname)
    person ={'username':username,
             'password':password,
             'email':email,
             'firstname':firstname,
             'lastname':lastname,
             'image':image_database.filename}
    user_collection.insert_one(person)
    return templates.TemplateResponse("login.html",{'request':request})


@app.get('/login',response_class=HTMLResponse)
def post_registration(request:Request):
    print("getlogin")
    
    return templates.TemplateResponse("login.html",{'request':request})


@app.post('/login',response_class=HTMLResponse)
def login_page(request:Request,username:str = Form(...),password:str = Form(...)):
   
    name = user_collection.find_one({'username':username,'password':password})
    if name:
        print("loggedin")
        global logged_in_user
        logged_in_user = username
        return RedirectResponse("/home")
    else:
        print("No login")
        return RedirectResponse('/login')


@app.post('/home', response_class=HTMLResponse)
def home_page(request: Request):

    posts_details = post_collection.find()

    user = user_collection.find_one({'username':logged_in_user})

    posts_dic=[]
    for pos in posts_details:
        name = user_collection.find_one({'username':pos['username']})

        posts_list ={
            'post_instance':pos,
            'id':pos["_id"],
            'username':pos['username'],
            'caption':pos['caption'],
            'description':pos['description'],
            'likes':len(pos['likes']),
            'comments':len(pos['comments']),
            'posted_user':name,
            'is_liked':False
        }

        if(logged_in_user in pos['likes']):
            posts_list['is_liked']=True
        
        if(pos['video_filename']==""):
            posts_list['image'] = pos['image_filename']
        else:
            posts_list['video'] = pos['video_filename']
        posts_dic.append(posts_list)

    return templates.TemplateResponse("home.html", {'request': request, 'user': user,"posts_dic":posts_dic})




@app.get('/home', response_class=HTMLResponse)
def home_page(request: Request):

    posts_details = post_collection.find()

    user = user_collection.find_one({'username':logged_in_user})

    posts_dic=[]
    for pos in posts_details:
        name = user_collection.find_one({'username':pos['username']})

        posts_list ={
            'post_instance':pos,
            'id':pos["_id"],
            'username':pos['username'],
            'caption':pos['caption'],
            'description':pos['description'],
            'likes':len(pos['likes']),
            'comments':len(pos['comments']),
            'posted_user':name,
            'is_liked':False
        }

        if(logged_in_user in pos['likes']):
            posts_list['is_liked']=True
        
        if(pos['video_filename']==""):
            posts_list['image'] = pos['image_filename']
        else:
            posts_list['video'] = pos['video_filename']
        posts_dic.append(posts_list)


    return templates.TemplateResponse("home.html", {'request': request, 'user': user,"posts_dic":posts_dic})





@app.get('/addpost',response_class=HTMLResponse)
def addpost(request:Request):
    return templates.TemplateResponse("create.html",{'request':request,'user':logged_in_user})



@app.post('/add_image',response_class = HTMLResponse)
def add_image(request:Request,
                    caption:str = Form(...),
                    description:str = Form(...),
                    image_database: UploadFile = File(...)):
    
    post = {'username':logged_in_user,
            'caption':caption,
            'description':description,
            'image_filename': image_database.filename,
            'video_filename': "",
            'likes':[],
            'comments':[],
            'created_at': datetime.now()
        }
    
    # print(post)
    post_collection.insert_one(post)
    return RedirectResponse('/home')



@app.post('/add_video',response_class = HTMLResponse)
def add_video(request:Request,
                    caption:str = Form(...),
                    description:str = Form(...),
                    video_database: UploadFile = File(...)):
    
    post = {'username':logged_in_user,
            'caption':caption,
            'description':description,
            'image_filename':"",
            'video_filename': video_database.filename,
            'likes':[],
            'comments':[],
            'created_at': datetime.now()
        }
    post_collection.insert_one(post)
    return RedirectResponse('/home')




@app.post("/likepost/{post_id}")
async def print_post_id(post_id: str):
    print(f"Clicked on image with Post ID: {post_id}")
    from bson.objectid import ObjectId
    id = ObjectId(post_id)
    global logged_in_user
    update_post = post_collection.find_one({"_id":id})
    if update_post:
        if logged_in_user in update_post['likes']:
            post_collection.update_one({"_id": id}, {"$pull": {"likes": logged_in_user}})
            return {"status": "success", "message": f"Removed {logged_in_user} from likes",'likes_count':len(update_post['likes'])-1,"mesage1":False}
        else:
            post_collection.update_one({"_id": id}, {"$push": {"likes": logged_in_user}})
            return {"status": "success", "message": f"Added {logged_in_user} to likes",'likes_count':len(update_post['likes'])+1,"mesage1":True}
    else:
        return {"status": "error", "message": "Post not found"}

    

@app.post("/add_comment/{post_id}")
async def add_comment(request: Request, post_id: str, comment_text: str = Form(...)):
    print(f"Received comment for Post ID {post_id}: {comment_text}")
    from bson.objectid import ObjectId
    id = ObjectId(post_id)
    global logged_in_user
   
    comment = {'user':logged_in_user,'text':comment_text,'created_at':datetime.now()}
    post_collection.update_one({"_id": id}, {"$push": {"comments": comment}})

    update_post = post_collection.find_one({"_id":id})
    print(update_post['comments'])

    return {"message": "Comment added successfully"}
    


@app.get('/showcomments/{post_id}')
def showcomments(request:Request,post_id:str):
    print("show comments called")
    global logged_in_user
    from bson.objectid import ObjectId
    id = ObjectId(post_id)
    post_instance = post_collection.find_one({'_id':id})
    user_instance =  user_collection.find_one({'username':post_instance['username']})
    logged_in = user_collection.find_one({'username':logged_in_user})
    comments =[]
    
    for com in post_instance['comments']:
        print("for loop")
        print("this is ",com)
        sub_com ={'com_user' : user_collection.find_one({'username':com['user']}),
                  'text':com['text'],
                  'created_at':com['created_at']}
        comments.append(sub_com)


    # for com in comments:
    #     print(com)
    # print(post_instance['image_filename'])
    return templates.TemplateResponse('showcomments.html',{'request':request,'post':post_instance,'post_user':user_instance,'user':logged_in,'comments':comments})
