from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.modules.router import api_router
from app.shared.config import settings
from app.shared.exception import BusinessError
from app.shared.exception_handler import validation_exception_handler, business_exception_handler

def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    
    Returns:
        FastAPI: 配置好的FastAPI应用实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        description="闲鱼媒体后端API服务",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(BusinessError, business_exception_handler)
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该配置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
 
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.get("/")
    async def root():
        """
        根路径健康检查
        
        Returns:
            dict: 应用信息
        """
        return {
            "message": "Welcome to Xianyu Media Backend API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    @app.get("/health")
    async def health_check():
        """
        健康检查端点
        
        Returns:
            dict: 健康状态
        """
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION
        }
    
    return app


# 创建应用实例
app = create_app()


def main():
    """
    主函数，用于开发环境启动
    """
    import uvicorn
    # 启动日志信息
    print("🚀 启动闲鱼媒体后端API服务...")
    print("📖 API文档地址: http://localhost:7000/docs")
    print("🔍 备用文档地址: http://localhost:7000/redoc")
    print("💚 健康检查地址: http://localhost:7000/health")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
