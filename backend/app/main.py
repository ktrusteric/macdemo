from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api import users, content, recommendations, ai_integration, region

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # CORS配置 - 更宽泛的配置以支持开发环境
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 开发环境允许所有来源
        allow_credentials=False,  # 当allow_origins为*时，必须为False
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        allow_headers=["*"],
    )
    
    # 注册路由
    application.include_router(
        users.router, 
        prefix=f"{settings.API_V1_STR}/users", 
        tags=["users"]
    )
    application.include_router(
        content.router, 
        prefix=f"{settings.API_V1_STR}/content", 
        tags=["content"]
    )
    application.include_router(
        recommendations.router, 
        prefix=f"{settings.API_V1_STR}/recommendations", 
        tags=["recommendations"]
    )
    application.include_router(
        ai_integration.router, 
        prefix=f"{settings.API_V1_STR}/ai", 
        tags=["ai"]
    )
    application.include_router(
        region.router, 
        prefix=f"{settings.API_V1_STR}/region", 
        tags=["region"]
    )
    
    # 添加用户行为记录路由
    application.include_router(
        users.router,
        prefix=f"{settings.API_V1_STR}/user-behavior",
        tags=["user-behavior"]
    )
    
    return application

app = create_application()

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Energy Info System API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Energy Info System is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 