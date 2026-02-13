"""元数据解析器：统一的 Frontmatter 解析和验证逻辑"""

from loguru import logger
import frontmatter

from .config_models import Config


class MetadataParser:
    """解析 Markdown 文件的 Frontmatter 元数据"""
    
    def __init__(self, config: Config):
        """初始化元数据解析器
        
        Args:
            config: 配置对象
        """
        self.config = config
        # 从配置读取默认值
        self.default_category = config.posts.defaults.category
        self.default_tags = config.posts.defaults.tags
        self.default_author = config.posts.defaults.author or config.site.author
    
    def parse(self, md_content: str) -> tuple[dict, str]:
        """解析 Frontmatter，返回 (元数据, 正文)
        
        Args:
            md_content: Markdown 文件内容
            
        Returns:
            tuple[dict, str]: (元数据字典, 正文内容)
        """
        try:
            post = frontmatter.loads(md_content)
            metadata = self.validate_metadata(post.metadata)
            return metadata, post.content
        except Exception as e:
            logger.warning(f"解析 Frontmatter 失败: {e}")
            return {}, md_content
    
    def validate_metadata(self, metadata: dict) -> dict:
        """标准化元数据字段（设置默认值、规范化格式）
        
        Args:
            metadata: 原始元数据字典
            
        Returns:
            dict: 标准化后的元数据字典
        """
        validated = metadata.copy()
        
        # 确保 title 存在
        if "title" not in validated:
            validated["title"] = "无标题"
        
        # 确保 tags 是列表
        if "tags" in validated:
            if isinstance(validated["tags"], str):
                validated["tags"] = [tag.strip() for tag in validated["tags"].split(",")]
            elif not isinstance(validated["tags"], list):
                validated["tags"] = [str(validated["tags"])]
        else:
            # 使用配置中的默认标签
            validated["tags"] = self.default_tags.copy()
        
        # 确保 category 存在
        if "category" not in validated:
            # 使用配置中的默认分类
            validated["category"] = self.default_category
        
        # 确保 author 存在
        if "author" not in validated:
            validated["author"] = self.default_author
        
        # 确保 date 存在
        if "date" not in validated:
            validated["date"] = ""
        
        # 标准化日期格式（如果是 datetime 对象，转为字符串）
        if hasattr(validated["date"], "strftime"):
            validated["date"] = validated["date"].strftime("%Y-%m-%d")
        
        # 确保 pinned 字段存在（用于置顶功能）
        if "pinned" not in validated:
            validated["pinned"] = False
        elif not isinstance(validated["pinned"], bool):
            # 如果不是布尔值，尝试转换
            validated["pinned"] = bool(validated["pinned"])
        
        return validated
