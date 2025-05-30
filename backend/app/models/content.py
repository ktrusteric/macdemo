from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

class ContentType(str, Enum):
    NEWS = "news"  # 行业资讯
    POLICY = "policy"  # 政策法规
    REPORT = "report"  # 研究报告
    ANNOUNCEMENT = "announcement"  # 交易公告
    PRICE = "price"  # 调价公告

class ContentTag(BaseModel):
    category: str
    name: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class Content(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    type: ContentType = ContentType.NEWS
    source: str = Field(default="官方发布", max_length=100)
    publish_time: datetime = Field(default_factory=datetime.utcnow)
    tags: List[ContentTag] = Field(default_factory=list)
    link: Optional[str] = None
    
    # 9大类标签字段
    basic_info_tags: List[str] = Field(default_factory=list, description="基础信息标签")
    region_tags: List[str] = Field(default_factory=list, description="地域标签（包含地区省份城市）")
    energy_type_tags: List[str] = Field(default_factory=list, description="能源品种标签")
    business_field_tags: List[str] = Field(default_factory=list, description="业务领域标签")
    beneficiary_tags: List[str] = Field(default_factory=list, description="受益主体标签")
    policy_measure_tags: List[str] = Field(default_factory=list, description="关键措施标签")
    importance_tags: List[str] = Field(default_factory=list, description="重要性标签")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 推荐相关字段
    relevance_score: Optional[float] = Field(None, description="相关性分数")
    view_count: int = Field(default=0, description="浏览次数") 