from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, Optional

class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    profile_image: Optional[str] = None
    followers: Optional[list] = []
    followings: Optional[list] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Comment(BaseModel):
    user: User
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)



class Post(BaseModel):
    user: User
    caption: Optional[str] = None
    location: Optional[str] = None
    likes: Optional[list] = []
    comments: Optional[list[Comment]] = []
    posted_at: datetime = Field(default_factory=datetime.utcnow)

