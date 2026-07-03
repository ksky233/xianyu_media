from .base import Base
from sqlalchemy import Column, String, Text, Integer, DateTime, BigInteger,NUMERIC
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
class Video(Base):
    """
    视频数据库模型
    
    用于存储视频的基本信息和资源链接
    """
    __tablename__ = "videos"
    
    # 主键ID
    id = Column(
        BigInteger, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="视频唯一标识符"
    )
    
    # 标题
    title = Column(
        String(255), 
        nullable=False, 
        index=True,
        comment="视频标题"
    )

    # 类型
    type = Column(
        String(100), 
        nullable=True, 
        index=True,
        comment="视频类型分类：电影/电视剧/动漫/短剧等"
    )

    # 封面图片URL
    cover_url = Column(
        Text, 
        nullable=True,
        comment="封面图片URL地址"
    )

    rating = Column(
        NUMERIC(3, 1), 
        nullable=True,
        comment="视频评分"
    )
    
    # 描述
    description = Column(
        Text, 
        nullable=True,
        comment="视频简短描述"
    )

    quality_tag = Column(
        String(100), 
        nullable=True,
        comment="视频质量标签：不仅包含1080P/720P/480P，还有WEB-DL等标签"
    )
    
    # 集数
    episode_count = Column(
        Integer, 
        nullable=True, 
        default=0,
        comment="视频总集数（除电影外几乎都有）"
    )
    
    # 演员
    actors = Column(
        Text, 
        nullable=True,
        comment="演员列表，多个演员用逗号分隔，动漫则为声优"
    )
    
    year = Column(
        Integer, 
        nullable=True,
        comment="上映年份"
    )
    
    
    # 百度网盘链接
    baidu_url = Column(
        Text, 
        nullable=True,
        comment="百度网盘资源链接"
    )
    
    # 夸克网盘链接
    quark_url = Column(
        Text, 
        nullable=True,
        comment="夸克网盘资源链接"
    )
    
    # 其他云盘链接
    other_cloud_url = Column(
        Text, 
        nullable=True,
        comment="其他云盘资源链接"
    )
    
    # 状态（整数类型）
    url_status = Column(
        Integer, 
        nullable=False, 
        default=1, 
        index=True,
        comment="网盘链接状态 0都失效,1主流 (百度/夸克) 有效,2 other盘有效,3都有效"
    )

    marketing_text = Column(
        Text, 
        nullable=True,
        comment="营销文本：闲鱼等平台推广文本"
    )

    hot_tags = Column(
        String(255), 
        nullable=True,
        comment="视频热门度标签，逗号分隔"
    )

    hot_score = Column(
        Integer, 
        nullable=True, 
        default=0,
        comment="视频热门度评分"
    )

    hot_reason = Column(
        Text, 
        nullable=True,
        comment="视频热门度评分原因"
    )

    region = Column(
        String(100), 
        nullable=True,
        comment="视频主要受众，如美剧/韩剧/日剧等"
    )

    finished = Column(
        Integer, 
        nullable=True, 
        default=0,
        comment="视频是否完结 0连载中,1已完结"
    )

    sale_status = Column(
        Integer, 
        nullable=True, 
        default=0,
        comment="视频上架状态 0未上架,1已上架"
    )



    extra_params = Column(
        JSONB, 
        nullable=True,
        comment="额外参数：JSON格式存储其他相关信息"
    )


    # 创建时间
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        index=True,
        comment="创建时间"
    )
    
    # 更新时间
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False,
        index=True,
        comment="最后更新时间"
    )
    
    # 删除时间（软删除）
    deleted_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        index=True,
        comment="删除时间，用于软删除"
    )
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', url_status={self.url_status}, type={self.type})>"
