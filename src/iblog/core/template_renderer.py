"""模板渲染器：封装 Jinja2 渲染逻辑"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    """使用 Jinja2 渲染 HTML 模板"""
    
    def __init__(self, template_dir: Path):
        """初始化模板渲染器
        
        Args:
            template_dir: 模板文件所在目录
        """
        self.template_dir = Path(template_dir)
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
    
    def _get_nav_links(self, depth: int) -> dict:
        """根据页面层级生成导航链接
        
        Args:
            depth: 页面层级，0=根目录, 1=一级子目录
            
        Returns:
            dict: 包含导航链接的字典
        """
        if depth == 0:
            return {
                "home": "index.html",
                "categories": "categories/index.html",
                "tags": "tags/index.html",
                "about": "about/index.html"
            }
        else:  # depth == 1
            return {
                "home": "../index.html",
                "categories": "../categories/index.html",
                "tags": "../tags/index.html",
                "about": "../about/index.html"
            }
    
    def _get_breadcrumb_links(self, current_section: str) -> dict:
        """根据当前页面类型生成面包屑导航链接
        
        Args:
            current_section: 当前页面所属区域（'categories' 或 'tags'）
            
        Returns:
            dict: 包含面包屑链接的字典
        """
        breadcrumb = {
            "home": "../index.html"
        }
        
        if current_section == "categories":
            breadcrumb["categories"] = "index.html"
        elif current_section == "tags":
            breadcrumb["tags"] = "index.html"
        
        return breadcrumb
    
    def render_post(self, content_html: str, metadata: dict, total_posts: int = 0) -> str:
        """渲染单篇博文页面
        
        Args:
            content_html: Markdown 转换后的 HTML 内容
            metadata: 文章元数据
            total_posts: 博客总数
            
        Returns:
            str: 完整的 HTML 页面
        """
        template = self.env.get_template("blog_post.html")
        return template.render(
            title=metadata.get("title", "无标题"),
            content_html=content_html,
            metadata=metadata,
            nav=self._get_nav_links(depth=1),
            total_posts=total_posts
        )
    
    def render_index(self, posts: list[dict], total_posts: int = 0) -> str:
        """渲染首页
        
        Args:
            posts: 文章列表（每个元素应包含 metadata 字段）
            total_posts: 博客总数
            
        Returns:
            str: 首页 HTML 内容
        """
        template = self.env.get_template("index.html")
        # 提取所有文章的 metadata
        posts_metadata = [post["metadata"] for post in posts]
        return template.render(
            posts=posts_metadata,
            nav=self._get_nav_links(depth=0),
            total_posts=total_posts
        )
    
    def render_categories(self, categories: list[dict], total_posts: int = 0) -> str:
        """渲染分类汇总页
        
        Args:
            categories: 分类列表，每个元素包含：
                - name: 分类名称
                - count: 文章数量
                - latest_post: 最新文章信息
                - url: 分类详情页链接
            total_posts: 博客总数
            
        Returns:
            str: 分类汇总页 HTML 内容
        """
        template = self.env.get_template("categories.html")
        return template.render(
            categories=categories,
            nav=self._get_nav_links(depth=1),
            total_posts=total_posts
        )
    
    def render_category_detail(self, category_name: str, posts: list[dict], total_posts: int = 0) -> str:
        """渲染单个分类的详情页
        
        Args:
            category_name: 分类名称
            posts: 该分类下的文章列表（包含 metadata 和 file_path）
            total_posts: 博客总数
            
        Returns:
            str: 分类详情页 HTML 内容
        """
        template = self.env.get_template("category_detail.html")
        # 为文章添加相对 URL（从 categories/ 目录访问 blogs/）
        posts_with_url = []
        for post in posts:
            metadata = post["metadata"].copy()
            metadata["url"] = f"../blogs/{post['file_path'].stem}.html"
            posts_with_url.append(metadata)
        
        return template.render(
            category_name=category_name,
            posts=posts_with_url,
            nav=self._get_nav_links(depth=1),
            breadcrumb=self._get_breadcrumb_links("categories"),
            total_posts=total_posts
        )
    
    def render_category_page(self, category: str, posts: list) -> str:
        """渲染分类页面（已弃用，使用 render_category_detail）
        
        Args:
            category: 分类名称
            posts: 该分类下的文章列表
            
        Returns:
            str: 分类页面 HTML 内容
        """
        # 为了向后兼容，调用新方法
        return self.render_category_detail(category, posts)
    
    def render_tags(self, tags: list[dict], total_posts: int = 0) -> str:
        """渲染标签云索引页
        
        Args:
            tags: 标签列表，每个元素包含：
                - name: 标签名称
                - count: 文章数量
                - url: 标签详情页链接
                - font_size: 字体大小（如 "1.2em"）
            total_posts: 博客总数
            
        Returns:
            str: 标签云页面 HTML 内容
        """
        template = self.env.get_template("tags.html")
        return template.render(
            tags=tags,
            nav=self._get_nav_links(depth=1),
            total_posts=total_posts
        )
    
    def render_tag_detail(self, tag_name: str, posts: list[dict], total_posts: int = 0) -> str:
        """渲染单个标签的详情页
        
        Args:
            tag_name: 标签名称
            posts: 该标签下的文章列表（包含 metadata 和 file_path）
            total_posts: 博客总数
            
        Returns:
            str: 标签详情页 HTML 内容
        """
        template = self.env.get_template("tag_detail.html")
        # 为文章添加相对 URL（从 tags/ 目录访问 blogs/）
        posts_with_url = []
        for post in posts:
            metadata = post["metadata"].copy()
            metadata["url"] = f"../blogs/{post['file_path'].stem}.html"
            posts_with_url.append(metadata)
        
        return template.render(
            tag_name=tag_name,
            posts=posts_with_url,
            nav=self._get_nav_links(depth=1),
            breadcrumb=self._get_breadcrumb_links("tags"),
            total_posts=total_posts
        )
    
    def render_tag_page(self, tag: str, posts: list) -> str:
        """渲染标签页面（已弃用，使用 render_tag_detail）
        
        Args:
            tag: 标签名称
            posts: 该标签下的文章列表
            
        Returns:
            str: 标签页面 HTML 内容
        """
        # 为了向后兼容，调用新方法
        return self.render_tag_detail(tag, posts)
    
    def render_about(self, content_html: str, metadata: dict, total_posts: int = 0) -> str:
        """渲染关于页面
        
        Args:
            content_html: Markdown 转换后的 HTML 内容
            metadata: 简化的元数据（只需 title）
            total_posts: 博客总数
            
        Returns:
            str: 完整的 HTML 页面
        """
        template = self.env.get_template("about.html")
        return template.render(
            title=metadata.get("title", "关于"),
            content_html=content_html,
            nav=self._get_nav_links(depth=1),
            total_posts=total_posts
        )
