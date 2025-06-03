from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

class ContentType(str, Enum):
    NEWS = "news"  # 行业资讯
    POLICY = "policy"  # 政策法规
    REPORT = "report"  # 研究报告
    ANNOUNCEMENT = "announcement"  # 交易公告
    PRICE = "price"  # 调价公告

# 内容类型映射（用于JSON导入）
CONTENT_TYPE_MAP = {
    "政策法规": ContentType.POLICY,
    "行业资讯": ContentType.NEWS,
    "调价公告": ContentType.PRICE,
    "交易公告": ContentType.ANNOUNCEMENT
}

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

# 文章创建请求模型
class ContentCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    type: ContentType = ContentType.NEWS
    source: str = Field(default="官方发布", max_length=100)
    publish_time: Optional[datetime] = None
    link: Optional[str] = None
    
    # 标签字段
    basic_info_tags: List[str] = Field(default_factory=list)
    region_tags: List[str] = Field(default_factory=list)
    energy_type_tags: List[str] = Field(default_factory=list)
    business_field_tags: List[str] = Field(default_factory=list)
    beneficiary_tags: List[str] = Field(default_factory=list)
    policy_measure_tags: List[str] = Field(default_factory=list)
    importance_tags: List[str] = Field(default_factory=list)

# 文章更新请求模型
class ContentUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    type: Optional[ContentType] = None
    source: Optional[str] = Field(None, max_length=100)
    publish_time: Optional[datetime] = None
    link: Optional[str] = None
    
    # 标签字段
    basic_info_tags: Optional[List[str]] = None
    region_tags: Optional[List[str]] = None
    energy_type_tags: Optional[List[str]] = None
    business_field_tags: Optional[List[str]] = None
    beneficiary_tags: Optional[List[str]] = None
    policy_measure_tags: Optional[List[str]] = None
    importance_tags: Optional[List[str]] = None

# JSON导入的文章模型
class JsonArticle(BaseModel):
    发布日期: str
    发布时间: str
    来源机构: str
    标题: str
    文章内容: str
    链接: Optional[str] = None
    基础信息标签: Optional[str] = None
    地域标签: Optional[str] = None
    能源品种标签: Optional[List[str]] = None
    业务领域标签: Optional[str] = None
    受益主体标签: Optional[str] = None
    关键措施标签: Optional[str] = None
    重要性标签: Optional[str] = None
    规范化地域标签: Optional[List[str]] = None

# 批量导入请求模型
class BatchImportRequest(BaseModel):
    articles: List[JsonArticle]
    auto_parse_tags: bool = Field(default=True, description="是否自动解析标签")
    overwrite_existing: bool = Field(default=False, description="是否覆盖已存在的文章")

# 批量导入响应模型
class BatchImportResponse(BaseModel):
    success: bool
    total_articles: int
    imported_count: int
    updated_count: int
    failed_count: int
    failed_articles: List[Dict[str, Any]] = Field(default_factory=list)
    message: str

# 文章管理响应模型
class ContentManagementResponse(BaseModel):
    success: bool
    data: Optional[Content] = None
    message: str 