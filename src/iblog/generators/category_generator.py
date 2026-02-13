"""分类生成器：生成按分类组织的文章视图（占位）"""

from pathlib import Path
from loguru import logger

from .base_generator import BaseGenerator


class CategoryGenerator(BaseGenerator):
    """生成分类视图页面"""
    
    def generate(self, posts: list[dict], output_dir: Path):
        """生成分类视图页面
        
        实现逻辑：
        1. 按分类分组文章
        2. 计算每个分类的统计信息
        3. 生成分类汇总页 categories/index.html
        4. 为每个分类生成详情页 categories/{分类名}.html
        
        Args:
            posts: 文章列表
            output_dir: 输出根目录
        """
        output_dir = Path(output_dir)
        categories_dir = output_dir / "categories"
        categories_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("开始生成分类视图")
        
        if len(posts) == 0:
            logger.warning("没有文章，跳过分类页面生成")
            return
        
        # 1. 按分类分组文章
        categories_dict = self._group_by_category(posts)
        logger.info(f"找到 {len(categories_dict)} 个分类")
        
        # 2. 计算每个分类的统计信息
        category_stats = []
        for name, cat_posts in categories_dict.items():
            latest_post = self._get_latest_post(cat_posts)
            category_stats.append({
                'name': name,
                'count': len(cat_posts),
                'latest_post': latest_post,
                'url': f'{name}.html'
            })
        
        # 按文章数量排序（数量多的在前）
        category_stats.sort(key=lambda x: x['count'], reverse=True)
        
        # 3. 生成分类汇总页
        self._render_category_index(category_stats, categories_dir, total_posts=len(posts))
        
        # 4. 为每个分类生成详情页
        for name, cat_posts in categories_dict.items():
            self._render_category_detail(name, cat_posts, categories_dir, total_posts=len(posts))
        
        logger.success(f"分类视图生成完成，共 {len(categories_dict)} 个分类")
    
    def _group_by_category(self, posts: list[dict]) -> dict[str, list]:
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
    
    def _get_latest_post(self, posts: list[dict]) -> dict:
        """获取该分类最新的文章
        
        Args:
            posts: 文章列表
            
        Returns:
            dict: 最新文章的元数据（title, date）
        """
        if not posts:
            return None
        
        # 按日期排序，取最新的
        sorted_posts = sorted(
            posts,
            key=lambda p: p["metadata"].get("date", ""),
            reverse=True
        )
        
        latest = sorted_posts[0]["metadata"]
        return {
            'title': latest.get('title', '无标题'),
            'date': latest.get('date', '')
        }
    
    def _render_category_index(self, category_stats: list[dict], categories_dir: Path, total_posts: int = 0):
        """渲染分类汇总页
        
        Args:
            category_stats: 分类统计信息列表
            categories_dir: categories 目录路径
            total_posts: 博客总数
        """
        html = self.renderer.render_categories(category_stats, total_posts=total_posts)
        
        index_path = categories_dir / "index.html"
        index_path.write_text(html, encoding="utf-8")
        
        logger.success(f"分类汇总页已生成: {index_path}")
    
    def _render_category_detail(self, category_name: str, posts: list[dict], categories_dir: Path, total_posts: int = 0):
        """渲染单个分类的详情页
        
        Args:
            category_name: 分类名称
            posts: 该分类下的文章列表
            categories_dir: categories 目录路径
            total_posts: 博客总数
        """
        # 按日期排序（最新的在前）
        sorted_posts = sorted(
            posts,
            key=lambda p: p["metadata"].get("date", ""),
            reverse=True
        )
        
        html = self.renderer.render_category_detail(category_name, sorted_posts, total_posts=total_posts)
        
        # 生成文件名
        output_path = categories_dir / f"{category_name}.html"
        output_path.write_text(html, encoding="utf-8")
        
        logger.debug(f"已生成分类页: {category_name} ({len(posts)} 篇文章)")
