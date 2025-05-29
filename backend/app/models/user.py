from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    FREE = "free"
    PAID = "paid"
    ADMIN = "admin"

class TagCategory(str, Enum):
    BASIC_INFO = "basic_info"
    CITY = "city"
    PROVINCE = "province"
    REGION = "region"
    ENERGY_TYPE = "energy_type"
    BUSINESS_FIELD = "business_field"
    BENEFICIARY = "beneficiary"
    POLICY_MEASURE = "policy_measure"
    IMPORTANCE = "importance"

class TagSource(str, Enum):
    PRESET = "preset"
    MANUAL = "manual"
    AI_GENERATED = "ai_generated"
    REGION_AUTO = "region_auto"
    AUTO = "auto"  # 添加通用的auto类型

class UserTag(BaseModel):
    category: Union[TagCategory, str]  # 支持枚举和字符串
    name: str = Field(..., min_length=1, max_length=100)
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    source: Union[TagSource, str] = TagSource.MANUAL  # 支持枚举和字符串
    created_at: Union[datetime, str] = Field(default_factory=datetime.utcnow)

    @validator('created_at', pre=True)
    def parse_created_at(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        return v or datetime.utcnow()

    @validator('category', pre=True)
    def validate_category(cls, v):
        # 接受字符串，如果不在枚举中就返回原值
        if isinstance(v, str):
            return v
        return v

    @validator('source', pre=True)
    def validate_source(cls, v):
        # 接受字符串，如果不在枚举中就返回原值
        if isinstance(v, str):
            return v
        return v

class UserTags(BaseModel):
    user_id: str = Field(..., description="用户ID")
    tags: List[UserTag] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 用户基础模型
class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: UserRole
    is_active: bool
    created_at: str
    has_initial_tags: bool = False
    register_city: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)
    register_city: str = Field(..., description="用户注册城市")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: UserRole
    is_active: bool
    created_at: str
    has_initial_tags: bool
    access_features: List[str] = []
    register_city: Optional[str] = None

# API响应模型
class UserTagsResponse(BaseModel):
    success: bool = True
    data: UserTags
    message: str = "Success"

class TagUpdateRequest(BaseModel):
    tags: List[UserTag]

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile