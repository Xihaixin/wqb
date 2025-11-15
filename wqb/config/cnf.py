import os
from pathlib import Path
from dotenv import load_dotenv

class enVars:
    _root_path = None  # 延迟初始化，避免类加载时依赖 __file__
    _env_loaded = False

    @classmethod
    def _get_root_path(cls) -> Path:
        """动态获取项目根路径（兼容 Jupyter 和普通脚本）"""
        if cls._root_path is None:
            try:
                # 方式1：普通 .py 脚本中，使用 __file__ 获取路径（原有逻辑）
                _current_dir = Path(__file__).parent
                cls._root_path = _current_dir.parent.parent
            except:
                # 方式2：Jupyter 中，使用当前工作目录推导（需确保 Jupyter 从项目根目录启动）
                _current_dir = Path.cwd().parent  # Jupyter 的当前工作目录
                cls._root_path = _current_dir.parent.parent
        return cls._root_path

    @classmethod
    def _get_env_path(cls) -> Path:
        """获取 .env 文件路径"""
        return cls._get_root_path() / ".env"

    @classmethod
    def _load_env_once(cls) -> None:
        """确保环境变量只加载一次"""
        if not cls._env_loaded:
            env_path = cls._get_env_path()
            if env_path.exists():
                load_dotenv(env_path)
            cls._env_loaded = True

    @classmethod
    def get_env_vars(cls) -> tuple[str, str]:
        """获取环境变量中的邮箱和密码"""
        cls._load_env_once()
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")

        if email is None:
            raise EnvironmentError("EMAIL environment variable is not set in .env file")
        if password is None:
            raise EnvironmentError("PASSWORD environment variable is not set in .env file")
        
        return (email, password)
    
    @classmethod
    def get_root_path(cls) -> Path:
        """获取项目根目录路径"""
        return cls._get_root_path()