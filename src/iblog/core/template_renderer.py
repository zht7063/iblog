"""模板渲染器：封装 Jinja2 渲染逻辑"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from .config_models import Config


class TemplateRenderer:
    """使用 Jinja2 渲染 HTML 模板"""
    
    def __init__(self, template_dir: Path, config: Config):
        """初始化模板渲染器
        
        Args:
            template_dir: 模板文件所在目录
            config: 配置对象
        """
        self.template_dir = Path(template_dir)
        self.config = config
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
    
    def _get_nav_links(self, depth: int) -> list[dict]:
        """根据页面层级生成导航链接（从配置或使用默认导航）
        
        Args:
            depth: 页面层级，0=根目录, 1=一级子目录
            
        Returns:
            list[dict]: 导航项列表，每项包含 name, url, icon
        """
        # 如果配置了自定义导航，使用配置
        if self.config.navigation:
            nav_items = []
            for item in self.config.navigation.items:
                url = item.url
                # 调整相对路径（如果是相对路径）
                if not url.startswith(('http://', 'https://', '/')):
                    if depth == 1 and not url.startswith('../'):
                        url = f"../{url}"
                nav_items.append({
                    'name': item.name,
                    'url': url,
                    'icon': item.icon
                })
            return nav_items
        
        # 否则使用默认导航（根据输出路径配置）
        paths = self.config.paths.output
        if depth == 0:
            return [
                {'name': '主页', 'url': 'index.html', 'icon': ''},
                {'name': '分组', 'url': f'{paths.categories}/index.html', 'icon': ''},
                {'name': '标签', 'url': f'{paths.tags}/index.html', 'icon': ''},
                {'name': '关于', 'url': f'{paths.about}/index.html', 'icon': ''}
            ]
        else:  # depth == 1
            return [
                {'name': '主页', 'url': '../index.html', 'icon': ''},
                {'name': '分组', 'url': f'../{paths.categories}/index.html', 'icon': ''},
                {'name': '标签', 'url': f'../{paths.tags}/index.html', 'icon': ''},
                {'name': '关于', 'url': f'../{paths.about}/index.html', 'icon': ''}
            ]
    
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
    
    def _get_global_context(self, depth: int) -> dict:
        """获取所有模板共享的全局上下文
        
        Args:
            depth: 页面层级，用于生成导航链接
            
        Returns:
            dict: 全局上下文，包含 site, footer, theme, navigation
        """
        return {
            'site': self.config.site.model_dump(),
            'footer': self.config.footer.model_dump(),
            'theme': self.config.theme.model_dump(),
            'navigation': self._get_nav_links(depth)
        }
    
    def render_post(self, content_html: str, metadata: dict, total_posts: int = 0, toc: list = None) -> str:
        """渲染单篇博文页面
        
        Args:
            content_html: Markdown 转换后的 HTML 内容
            metadata: 文章元数据
            total_posts: 博客总数
            toc: 目录列表，每项包含 level, text, id
            
        Returns:
            str: 完整的 HTML 页面
        """
        template = self.env.get_template("blog_post.html")
        # 合并全局上下文和页面特定数据
        context = self._get_global_context(depth=1)
        context.update({
            'title': metadata.get("title", "无标题"),
            'content_html': content_html,
            'metadata': metadata,
            'total_posts': total_posts,
            'toc': toc or []
        })
        return template.render(**context)
    
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
        # 合并全局上下文
        context = self._get_global_context(depth=0)
        context.update({
            'posts': posts_metadata,
            'total_posts': total_posts
        })
        return template.render(**context)
    
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
        context = self._get_global_context(depth=1)
        context.update({
            'categories': categories,
            'total_posts': total_posts
        })
        return template.render(**context)
    
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
        # 为文章添加相对 URL（使用配置的路径）
        posts_dir = self.config.paths.output.posts
        posts_with_url = []
        for post in posts:
            metadata = post["metadata"].copy()
            metadata["url"] = f"../{posts_dir}/{post['file_path'].stem}.html"
            posts_with_url.append(metadata)
        
        context = self._get_global_context(depth=1)
        context.update({
            'category_name': category_name,
            'posts': posts_with_url,
            'breadcrumb': self._get_breadcrumb_links("categories"),
            'total_posts': total_posts
        })
        return template.render(**context)
    
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
        context = self._get_global_context(depth=1)
        context.update({
            'tags': tags,
            'total_posts': total_posts
        })
        return template.render(**context)
    
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
        # 为文章添加相对 URL（使用配置的路径）
        posts_dir = self.config.paths.output.posts
        posts_with_url = []
        for post in posts:
            metadata = post["metadata"].copy()
            metadata["url"] = f"../{posts_dir}/{post['file_path'].stem}.html"
            posts_with_url.append(metadata)
        
        context = self._get_global_context(depth=1)
        context.update({
            'tag_name': tag_name,
            'posts': posts_with_url,
            'breadcrumb': self._get_breadcrumb_links("tags"),
            'total_posts': total_posts
        })
        return template.render(**context)
    
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
        context = self._get_global_context(depth=1)
        context.update({
            'title': metadata.get("title", "关于"),
            'content_html': content_html,
            'total_posts': total_posts
        })
        return template.render(**context)
