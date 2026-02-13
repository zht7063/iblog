"""配置模型定义（基于 Pydantic）

使用 Pydantic 提供类型安全的配置管理，支持：
- 类型检查和自动验证
- 默认值处理
- 清晰的错误提示
- IDE 代码补全
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


# ========================================
# 站点配置
# ========================================
class SiteConfig(BaseModel):
    """站点基础信息配置"""
    title: str
    subtitle: str
    author: str
    start_date: str
    description: str = ""
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"
    url: str = ""


# ========================================
# 导航配置
# ========================================
class NavigationItem(BaseModel):
    """导航项"""
    name: str
    url: str
    icon: str = ""


class NavigationConfig(BaseModel):
    """导航栏配置"""
    items: list[NavigationItem]


# ========================================
# 页脚配置
# ========================================
class SocialLink(BaseModel):
    """社交链接"""
    name: str
    url: str
    icon: str = ""


class FooterConfig(BaseModel):
    """页脚配置"""
    copyright: str
    show_powered_by: bool = True
    powered_by_text: str = "iblog"
    show_run_days: bool = True
    show_post_count: bool = True
    social_links: list[SocialLink] = Field(default_factory=list)


# ========================================
# 主题配置
# ========================================
class ThemeColorsConfig(BaseModel):
    """主题颜色配置"""
    background: str = "rgb(250, 249, 245)"
    text: str = "#000"
    link: str = "#000"
    border: str = "#ddd"
    hover_bg: str = "rgba(0, 0, 0, 0.04)"
    text_secondary: str = "#666"


class ThemeLayoutConfig(BaseModel):
    """主题布局配置"""
    max_width: str = "900px"
    padding: str = "20px"
    padding_mobile: str = "15px"


class ThemeFontsConfig(BaseModel):
    """主题字体配置"""
    body: str = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    code: str = "Monaco, Consolas, 'Courier New', monospace"
    heading: str = ""


class ThemeCDNConfig(BaseModel):
    """主题 CDN 资源配置"""
    markdown_css: str = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css"


class ThemeConfig(BaseModel):
    """主题配置"""
    colors: ThemeColorsConfig = Field(default_factory=ThemeColorsConfig)
    layout: ThemeLayoutConfig = Field(default_factory=ThemeLayoutConfig)
    fonts: ThemeFontsConfig = Field(default_factory=ThemeFontsConfig)
    cdn: ThemeCDNConfig = Field(default_factory=ThemeCDNConfig)


# ========================================
# 功能开关配置
# ========================================
class GeneratorsConfig(BaseModel):
    """生成器开关配置"""
    index: bool = True
    posts: bool = True
    categories: bool = True
    tags: bool = True
    about: bool = True


class PaginationConfig(BaseModel):
    """分页配置"""
    enabled: bool = False
    posts_per_page: int = 10


class PostCardConfig(BaseModel):
    """文章卡片显示配置"""
    show_description: bool = True
    show_category: bool = True
    show_tags: bool = True
    show_date: bool = True
    show_updated: bool = True
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M"


class FeaturesConfig(BaseModel):
    """功能配置"""
    generators: GeneratorsConfig = Field(default_factory=GeneratorsConfig)
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)
    post_card: PostCardConfig = Field(default_factory=PostCardConfig)


# ========================================
# 路径配置
# ========================================
class PathsOutputConfig(BaseModel):
    """输出路径配置"""
    posts: str = "blogs"
    categories: str = "categories"
    tags: str = "tags"
    about: str = "about"
    assets: str = "assets"


class PathsConfig(BaseModel):
    """路径配置"""
    output: PathsOutputConfig = Field(default_factory=PathsOutputConfig)


# ========================================
# 文章配置
# ========================================
class PostsSortConfig(BaseModel):
    """文章排序配置"""
    by: Literal["date", "updated", "title"] = "date"
    order: Literal["asc", "desc"] = "desc"


class PostsDefaultsConfig(BaseModel):
    """文章默认值配置"""
    category: str = "未分类"
    tags: list[str] = Field(default_factory=list)
    author: str = ""


class PostsExcerptConfig(BaseModel):
    """文章摘要配置"""
    auto_generate: bool = False
    length: int = 200
    suffix: str = "..."


class PostsConfig(BaseModel):
    """文章配置"""
    sort: PostsSortConfig = Field(default_factory=PostsSortConfig)
    defaults: PostsDefaultsConfig = Field(default_factory=PostsDefaultsConfig)
    excerpt: PostsExcerptConfig = Field(default_factory=PostsExcerptConfig)


# ========================================
# 日志配置
# ========================================
class LoggingFileConfig(BaseModel):
    """日志文件配置"""
    enabled: bool = False
    path: str = "logs/iblog.log"


class LoggingConfig(BaseModel):
    """日志配置"""
    level: Literal["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR"] = "INFO"
    console: bool = True
    file: LoggingFileConfig = Field(default_factory=LoggingFileConfig)
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"


# ========================================
# 构建配置
# ========================================
class BuildConfig(BaseModel):
    """构建配置"""
    clean_output: bool = False
    copy_assets: bool = False
    exclude: list[str] = Field(default_factory=lambda: ["*.tmp", "*.draft", "_*", ".git"])
    incremental: bool = False
    parallel: bool = False


# ========================================
# 根配置
# ========================================
class Config(BaseModel):
    """iblog 完整配置模型"""
    site: SiteConfig
    navigation: Optional[NavigationConfig] = None
    footer: FooterConfig
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    posts: PostsConfig = Field(default_factory=PostsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    build: BuildConfig = Field(default_factory=BuildConfig)
    
    class Config:
        """Pydantic 配置"""
        extra = "allow"  # 允许额外字段（未来扩展）
