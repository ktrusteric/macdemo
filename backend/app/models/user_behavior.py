from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class UserFavorite(BaseModel):
    """用户收藏文章模型"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(..., description="用户ID")
    content_id: str = Field(..., description="文章ID")
    favorited_at: datetime = Field(default_factory=datetime.now, description="收藏时间")
    
    # 收藏时文章的标签快照（用于标签学习）
    energy_type_tags: List[str] = Field(default=[], description="能源类型标签快照")
    region_tags: List[str] = Field(default=[], description="地域标签快照")
    business_field_tags: List[str] = Field(default=[], description="业务领域标签快照")
    
    # 标签学习状态
    tags_learned: bool = Field(default=False, description="是否已学习标签")
    learned_at: Optional[datetime] = Field(default=None, description="标签学习时间")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserBehaviorStats(BaseModel):
    """用户行为统计"""
    user_id: str = Field(..., description="用户ID")
    total_favorites: int = Field(default=0, description="总收藏数")
    energy_type_interests: dict = Field(default={}, description="能源类型兴趣分布")
    region_interests: dict = Field(default={}, description="地域兴趣分布")
    last_activity: Optional[datetime] = Field(default=None, description="最后活动时间")
    
class FavoriteRequest(BaseModel):
    """收藏请求模型"""
    content_id: str = Field(..., description="文章ID")
    
class FavoriteResponse(BaseModel):
    """收藏响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作结果消息")
    learned_tags: Optional[dict] = Field(default=None, description="新学习的标签")
    total_favorites: int = Field(default=0, description="用户总收藏数") 