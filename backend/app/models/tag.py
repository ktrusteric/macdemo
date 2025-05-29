from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TagLibrary(BaseModel):
    id: Optional[str] = None
    category: str  # 标签类别
    name: str  # 标签名称
    description: Optional[str] = None
    usage_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 