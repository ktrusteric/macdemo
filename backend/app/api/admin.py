from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from app.models.user import AdminLoginRequest, AdminLoginResponse, UserProfile, AdminPermission
from app.models.content import (
    Content, ContentCreateRequest, ContentUpdateRequest, 
    BatchImportRequest, BatchImportResponse, ContentManagementResponse,
    JsonArticle
)
from app.services.admin_service import AdminService
from app.services.user_service import UserService
from app.core.security import create_access_token, verify_password
from app.core.database import get_database
from datetime import timedelta
from app.core.config import settings
import logging
import json
from jose import JWTError, jwt
from pydantic import BaseModel
from ..services.dify_service import dify_service
from fastapi.responses import JSONResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# 响应模型
class AdminUserResponse(BaseModel):
    """管理员用户信息响应模型"""
    id: str
    username: str
    email: str
    register_city: Optional[str]
    role: str
    is_active: bool
    created_at: str
    tags_count: int

class AdminUsersListResponse(BaseModel):
    """管理员用户列表响应模型"""
    data: List[AdminUserResponse]
    total: int
    page: int
    page_size: int

# 管理员权限验证依赖
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
):
    """验证管理员身份"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        
        if user_id is None or user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的管理员凭证"
            )
        
        # 检查是否是内置管理员账户
        if user_id.startswith("builtin_admin_"):
            # 内置管理员账户，直接验证通过
            admin_service = AdminService(db)
            username = user_id.replace("builtin_admin_", "")
            
            # 从内置账户配置中获取信息
            from app.services.admin_service import BUILTIN_ADMIN_ACCOUNTS
            admin_account = None
            for account_key, account_info in BUILTIN_ADMIN_ACCOUNTS.items():
                if account_info["username"] == username:
                    admin_account = account_info
                    break
            
            if not admin_account:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="内置管理员账户不存在"
                )
            
            return {
                "user_id": user_id,
                "username": admin_account["username"],
                "role": user_role
            }
        else:
            # 数据库中的管理员用户
            admin_service = AdminService(db)
            user_doc = await admin_service.users_collection.find_one({"_id": user_id, "role": "admin"})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="管理员用户不存在"
                )
            
            return {
                "user_id": user_id,
                "username": user_doc.get("username"),
                "role": user_role
            }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    login_request: AdminLoginRequest,
    db = Depends(get_database)
):
    """管理员登录"""
    logger.info(f"🔐 管理员登录尝试 - username: {login_request.username}")
    
    try:
        admin_service = AdminService(db)
        
        # 验证管理员凭证
        admin_user = await admin_service.authenticate_admin(
            login_request.username, 
            login_request.password
        )
        
        if not admin_user:
            logger.warning(f"❌ 管理员登录失败 - 用户名或密码错误: {login_request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": admin_user.id, "role": admin_user.role},
            expires_delta=access_token_expires
        )
        
        # 获取管理员权限
        permissions = admin_service.get_admin_permissions(admin_user.role)
        
        # 构建用户资料
        admin_profile = UserProfile(
            id=admin_user.id,
            email=admin_user.email,
            username=admin_user.username,
            role=admin_user.role,
            is_active=admin_user.is_active,
            created_at=admin_user.created_at,
            has_initial_tags=admin_user.has_initial_tags,
            access_features=permissions,
            register_city=admin_user.register_city
        )
        
        logger.info(f"✅ 管理员登录成功: {admin_user.username}")
        
        return AdminLoginResponse(
            access_token=access_token,
            token_type="bearer",
            admin=admin_profile,
            permissions=permissions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 管理员登录异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录服务异常"
        )

@router.get("/articles", response_model=Dict[str, Any])
async def get_articles_for_management(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None, description="内容类型筛选"),
    energy_type: Optional[str] = Query(None, description="能源类型筛选"),
    search_keyword: Optional[str] = Query(None, description="搜索关键词"),
    tag_search: Optional[str] = Query(None, description="标签搜索"),
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """获取文章管理列表"""
    logger.info(f"📋 管理员获取文章列表 - admin: {current_admin['username']}, page: {page}")
    logger.info(f"🔍 搜索参数 - content_type: {content_type}, energy_type: {energy_type}, search_keyword: {search_keyword}, tag_search: {tag_search}")
    
    try:
        admin_service = AdminService(db)
        result = await admin_service.get_articles_for_management(
            page=page,
            page_size=page_size,
            content_type=content_type,
            energy_type=energy_type,
            search_keyword=search_keyword,
            tag_search=tag_search
        )
        
        # 🔥 修复：确保每个文章都有正确的id字段，删除_id字段
        if 'items' in result:
            for item in result['items']:
                if isinstance(item, dict):
                    # 如果有_id但没有id，则设置id
                    if '_id' in item and ('id' not in item or item.get('id') is None):
                        item['id'] = item['_id']
                    # 删除_id字段，避免混淆
                    if '_id' in item:
                        del item['_id']
        
        logger.info(f"✅ 获取文章列表成功 - 返回 {len(result['items'])} 篇文章")
        
        # 🔥 使用JSONResponse直接返回，绕过FastAPI的Pydantic序列化
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ 获取文章列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文章列表失败: {str(e)}"
        )

@router.post("/articles", response_model=ContentManagementResponse)
async def create_article(
    article_data: ContentCreateRequest,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """创建文章"""
    logger.info(f"📝 管理员创建文章 - admin: {current_admin['username']}, title: {article_data.title}")
    
    try:
        admin_service = AdminService(db)
        content = await admin_service.create_article(article_data, current_admin['user_id'])
        
        return ContentManagementResponse(
            success=True,
            data=content,
            message="文章创建成功"
        )
        
    except Exception as e:
        logger.error(f"❌ 创建文章失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建文章失败: {str(e)}"
        )

@router.put("/articles/{article_id}", response_model=ContentManagementResponse)
async def update_article(
    article_id: str,
    update_data: ContentUpdateRequest,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """更新文章"""
    logger.info(f"✏️ 管理员更新文章 - admin: {current_admin['username']}, article_id: {article_id}")
    
    try:
        admin_service = AdminService(db)
        content = await admin_service.update_article(article_id, update_data, current_admin['user_id'])
        
        return ContentManagementResponse(
            success=True,
            data=content,
            message="文章更新成功"
        )
        
    except Exception as e:
        logger.error(f"❌ 更新文章失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新文章失败: {str(e)}"
        )

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """删除文章"""
    logger.info(f"🗑️ 管理员删除文章 - admin: {current_admin['username']}, article_id: {article_id}")
    
    try:
        admin_service = AdminService(db)
        success = await admin_service.delete_article(article_id, current_admin['user_id'])
        
        if success:
            return {"success": True, "message": "文章删除成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在或删除失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除文章失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文章失败: {str(e)}"
        )

@router.post("/articles/batch-import", response_model=BatchImportResponse)
async def batch_import_articles(
    import_request: BatchImportRequest,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """批量导入文章"""
    logger.info(f"📦 管理员批量导入文章 - admin: {current_admin['username']}, count: {len(import_request.articles)}")
    
    try:
        admin_service = AdminService(db)
        result = await admin_service.batch_import_articles(
            articles=import_request.articles,
            admin_id=current_admin['user_id'],
            auto_parse_tags=import_request.auto_parse_tags,
            overwrite_existing=import_request.overwrite_existing
        )
        
        return BatchImportResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ 批量导入文章失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入文章失败: {str(e)}"
        )

@router.post("/articles/import-json-file")
async def import_json_file(
    file: UploadFile = File(...),
    auto_parse_tags: bool = Query(True, description="是否自动解析标签"),
    overwrite_existing: bool = Query(False, description="是否覆盖已存在的文章"),
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """从JSON文件导入文章"""
    logger.info(f"📁 管理员从文件导入文章 - admin: {current_admin['username']}, file: {file.filename}")
    
    try:
        # 检查文件类型
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持JSON文件格式"
            )
        
        # 读取文件内容
        content = await file.read()
        try:
            json_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON文件格式错误: {str(e)}"
            )
        
        # 转换为JsonArticle对象列表
        articles = []
        if isinstance(json_data, list):
            for item in json_data:
                try:
                    articles.append(JsonArticle(**item))
                except Exception as e:
                    logger.warning(f"跳过无效的文章数据: {str(e)}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON文件应包含文章数组"
            )
        
        if not articles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未找到有效的文章数据"
            )
        
        # 执行批量导入
        admin_service = AdminService(db)
        result = await admin_service.batch_import_articles(
            articles=articles,
            admin_id=current_admin['user_id'],
            auto_parse_tags=auto_parse_tags,
            overwrite_existing=overwrite_existing
        )
        
        return BatchImportResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 从文件导入文章失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"从文件导入文章失败: {str(e)}"
        )

@router.get("/articles/{article_id}", response_model=Content)
async def get_article_detail(
    article_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """获取文章详情"""
    logger.info(f"📄 管理员获取文章详情 - admin: {current_admin['username']}, article_id: {article_id}")
    
    try:
        admin_service = AdminService(db)
        from bson import ObjectId
        
        article_doc = await admin_service.content_collection.find_one({"_id": ObjectId(article_id)})
        if not article_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
        
        article_doc["id"] = str(article_doc["_id"])
        content = Content(**article_doc)
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取文章详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文章详情失败: {str(e)}"
        )

@router.get("/stats")
async def get_admin_stats(
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """获取管理员统计数据"""
    logger.info(f"📊 管理员获取统计数据 - admin: {current_admin['username']}")
    
    try:
        admin_service = AdminService(db)
        
        # 获取文章统计
        total_articles = await admin_service.content_collection.count_documents({})
        
        # 按类型统计
        pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        type_stats = {}
        async for doc in admin_service.content_collection.aggregate(pipeline):
            type_stats[doc["_id"]] = doc["count"]
        
        # 获取用户统计 - 修复：删除普通用户相关查询
        # 数据库中的用户（演示用户，角色为"free"）
        db_users_total = await admin_service.users_collection.count_documents({})
        db_admin_users = await admin_service.users_collection.count_documents({"role": "admin"})
        
        # 内置管理员账户数量（不在数据库中）
        builtin_admins = 2  # superadmin 和 admin
        
        # 实际统计
        total_users = db_users_total + builtin_admins
        admin_users = db_admin_users + builtin_admins
        
        stats = {
            "articles": {
                "total": total_articles,
                "by_type": type_stats
            },
            "users": {
                "total": total_users,
                "admins": admin_users
            }
        }
        
        logger.info(f"✅ 获取统计数据成功 - 文章:{total_articles}, 用户:{total_users}(管理员:{admin_users})")
        return stats
        
    except Exception as e:
        logger.error(f"❌ 获取统计数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )

@router.get("/users", response_model=AdminUsersListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """获取用户列表"""
    logger.info(f"📋 管理员获取用户列表 - admin: {current_admin['username']}, page: {page}")
    
    try:
        user_service = UserService(db)
        result = await user_service.get_users(
            page=page,
            page_size=page_size
        )
        
        logger.info(f"✅ 获取用户列表成功 - 返回 {len(result['data'])} 个用户")
        return result
        
    except Exception as e:
        logger.error(f"❌ 获取用户列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )

@router.post("/articles/generate-tags")
async def generate_article_tags(
    request: dict,
    current_admin = Depends(get_current_admin)
):
    """使用Dify API生成文章标签"""
    try:
        article_content = request.get("content", "")
        if not article_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文章内容不能为空"
            )
        
        logger.info(f"🤖 管理员 {current_admin['username']} 请求生成文章标签")
        
        # 调用Dify服务生成标签
        tags_data = await dify_service.generate_article_tags(article_content)
        
        return {
            "success": True,
            "data": tags_data,
            "message": "标签生成成功"
        }
        
    except Exception as e:
        logger.error(f"❌ 生成文章标签失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成文章标签失败: {str(e)}"
        ) 