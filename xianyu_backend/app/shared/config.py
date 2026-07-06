from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    """
    应用程序配置类
    """
    # API Token配置
    API_TOKEN_SECRET_KEY: str
    API_TOKEN_ALGORITHM: str = "HS256"
    API_TOKEN_PREFIX: str = "api_"

    # JWT配置
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    API_V1_STR: str = "/api/v1" # API 的前缀
    
    # 数据库配置
    DATABASE_URL: str
    
    # 应用配置
    APP_NAME: str = "Xianyu Media Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # AI API 配置
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ARK_API_KEY: str = ""
    ARK_API_BASE: str = "https://ark.cn-beijing.volces.com/api/v3"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()