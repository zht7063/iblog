"""基础生成器：所有生成器的抽象基类"""

from pathlib import Path
from markdown_it import MarkdownIt

from iblog.core.template_renderer import TemplateRenderer
from iblog.core.config_models import Config


class BaseGenerator:
    """生成器基类，定义统一接口"""
    
    def __init__(self, renderer: TemplateRenderer, config: Config):
        """初始化生成器
        
        Args:
            renderer: 模板渲染器实例
            config: 配置对象
        """
        self.renderer = renderer
        self.config = config
        self.md_parser = MarkdownIt("gfm-like")
    
    def generate(self, posts: list[dict], output_dir: Path):
        """生成器的核心方法
        
        Args:
            posts: 文章列表
            output_dir: 输出目录
        """
        raise NotImplementedError("子类必须实现 generate 方法")
