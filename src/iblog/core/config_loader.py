"""配置加载器

从 YAML 文件加载配置并使用 Pydantic 进行验证
"""

import yaml
from pathlib import Path
from loguru import logger
from pydantic import ValidationError

from .config_models import Config


class ConfigLoader:
    """配置加载器，负责从 YAML 文件加载和验证配置"""
    
    @staticmethod
    def load(config_path: Path) -> Config:
        """从 YAML 文件加载配置并验证
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Config: 验证后的配置对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置验证失败
            yaml.YAMLError: YAML 格式错误
        """
        # 检查文件是否存在
        if not config_path.exists():
            error_msg = f"配置文件不存在: {config_path}\n请确保项目根目录有 config.yaml 文件"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # 读取 YAML 文件
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            error_msg = f"YAML 格式错误: {e}"
            logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"读取配置文件失败: {e}"
            logger.error(error_msg)
            raise
        
        # 使用 Pydantic 验证并构造配置对象
        try:
            config = Config(**raw_config)
            logger.success(f"✓ 配置加载成功: {config_path}")
            logger.debug(f"站点标题: {config.site.title}")
            logger.debug(f"启用的生成器: index={config.features.generators.index}, "
                        f"posts={config.features.generators.posts}, "
                        f"categories={config.features.generators.categories}, "
                        f"tags={config.features.generators.tags}, "
                        f"about={config.features.generators.about}")
            return config
        except ValidationError as e:
            error_msg = f"配置验证失败:\n{e}"
            logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"配置加载失败: {e}"
            logger.error(error_msg)
            raise
    
    @staticmethod
    def load_from_cwd() -> Config:
        """从当前工作目录加载 config.yaml
        
        Returns:
            Config: 验证后的配置对象
        """
        config_path = Path.cwd() / "config.yaml"
        return ConfigLoader.load(config_path)
