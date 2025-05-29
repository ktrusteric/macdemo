from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

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
    id: Optional[str] = None
    title: str
    content: str
    type: ContentType
    source: str  # 来源机构
    tags: List[ContentTag]
    publish_time: datetime
    author: Optional[str] = None
    link: Optional[str] = None
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 7大类标签字段
    basic_info_tags: List[str] = Field(default_factory=list)
    region_tags: List[str] = Field(default_factory=list)
    energy_type_tags: List[str] = Field(default_factory=list)
    business_field_tags: List[str] = Field(default_factory=list)
    beneficiary_tags: List[str] = Field(default_factory=list)
    policy_measure_tags: List[str] = Field(default_factory=list)
    importance_tags: List[str] = Field(default_factory=list)
    
    # 推荐相关字段
    relevance_score: Optional[float] = Field(None, description="相关性分数")
    view_count: int = Field(default=0, description="浏览次数") 