"""文件扫描器：扫描 Markdown 文件并构建文章列表"""

from pathlib import Path
from loguru import logger

from .metadata_parser import MetadataParser
from .config_models import Config


class FileScanner:
    """扫描目录下的 Markdown 文件并提取元数据"""
    
    def __init__(self, parser: MetadataParser, config: Config):
        """初始化文件扫描器
        
        Args:
            parser: 元数据解析器实例
            config: 配置对象
        """
        self.parser = parser
        self.config = config
    
    def scan_directory(self, md_dir: Path, exclude_files: list[str] = None) -> list[dict]:
        """扫描目录，返回所有文章的元数据列表
        
        Args:
            md_dir: Markdown 文件所在目录
            exclude_files: 要排除的文件名列表（默认排除 about.md）
            
        Returns:
            list[dict]: 文章列表，每个元素包含：
                - file_path: Path 对象
                - metadata: 元数据字典
                - content: 正文内容
        """
        md_dir = Path(md_dir)
        posts = []
        
        # 默认排除 about.md 等特殊页面
        if exclude_files is None:
            exclude_files = ["about.md"]
        
        logger.info(f"开始扫描目录: {md_dir}")
        
        for md_file in md_dir.glob("*.md"):
            # 跳过排除列表中的文件
            if md_file.name in exclude_files:
                logger.debug(f"跳过特殊文件: {md_file.name}")
                continue
            
            try:
                md_content = md_file.read_text(encoding="utf-8")
                metadata, content = self.parser.parse(md_content)
                
                posts.append({
                    "file_path": md_file,
                    "metadata": metadata,
                    "content": content
                })
                
                logger.debug(f"扫描文件: {md_file.name} - {metadata.get('title', '无标题')}")
            except Exception as e:
                logger.warning(f"处理文件 {md_file} 时出错: {e}")
                continue
        
        logger.info(f"扫描完成，找到 {len(posts)} 篇文章")
        return posts
    
    def sort_by_date(self, posts: list[dict], reverse: bool = True) -> list[dict]:
        """按日期排序文章列表
        
        Args:
            posts: 文章列表
            reverse: 是否降序排列（默认 True，最新的在前）
            
        Returns:
            list[dict]: 排序后的文章列表
        """
        return sorted(
            posts,
            key=lambda p: p["metadata"].get("date", ""),
            reverse=reverse
        )
    
    def sort_by_pinned_and_date(self, posts: list[dict], reverse: bool = True) -> list[dict]:
        """按置顶状态和配置的排序方式排序文章列表（置顶文章优先）
        
        Args:
            posts: 文章列表
            reverse: 是否降序排列（默认 True），会被配置覆盖
            
        Returns:
            list[dict]: 排序后的文章列表（置顶文章在前，然后按配置排序）
        """
        # 从配置读取排序方式
        sort_by = self.config.posts.sort.by  # "date" | "updated" | "title"
        sort_order = self.config.posts.sort.order  # "asc" | "desc"
        reverse = (sort_order == "desc")
        
        # 根据配置选择排序字段
        if sort_by == "updated":
            sort_key = lambda p: p["metadata"].get("updated", p["metadata"].get("date", ""))
        elif sort_by == "title":
            sort_key = lambda p: p["metadata"].get("title", "")
        else:  # date (默认)
            sort_key = lambda p: p["metadata"].get("date", "")
        
        # 先按配置的字段排序
        sorted_posts = sorted(posts, key=sort_key, reverse=reverse)
        
        # 再按置顶状态排序（稳定排序，保持原有顺序）
        sorted_posts = sorted(
            sorted_posts,
            key=lambda p: not p["metadata"].get("pinned", False)
        )
        
        return sorted_posts
    
    def group_by_category(self, posts: list[dict]) -> dict[str, list]:
        """按分类分组文章
        
        Args:
            posts: 文章列表
            
        Returns:
            dict[str, list]: 分类名到文章列表的映射
        """
        categories = {}
        
        for post in posts:
            category = post["metadata"].get("category", "未分类")
            if category not in categories:
                categories[category] = []
            categories[category].append(post)
        
        return categories
    
    def group_by_tags(self, posts: list[dict]) -> dict[str, list]:
        """按标签分组文章（一篇文章可以属于多个标签）
        
        Args:
            posts: 文章列表
            
        Returns:
            dict[str, list]: 标签名到文章列表的映射
        """
        tags = {}
        
        for post in posts:
            post_tags = post["metadata"].get("tags", [])
            for tag in post_tags:
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(post)
        
        return tags
