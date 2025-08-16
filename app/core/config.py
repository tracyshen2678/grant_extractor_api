# app/core/config.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. 获取项目根目录的绝对路径
# Path(__file__) -> 当前文件 (config.py) 的路径
# .parent -> 当前文件所在的文件夹 (core/)
# .parent -> 再上一级文件夹 (app/)
# .parent -> 再上一级文件夹 (项目的根目录)
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = ROOT_DIR / ".env" # 使用 / 操作符来安全地拼接路径

class Settings(BaseSettings):
    # 2. 直接告诉 pydantic-settings .env 文件的绝对路径
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding='utf-8')

    LLAMA_CLOUD_API_KEY: str
    OPENAI_API_KEY: str

# 3. (调试用) 确认一下路径是否正确
print(f"--- [Config] 正在从以下路径加载 .env 文件: {ENV_FILE_PATH} ---")

# 创建一个全局可用的配置实例
settings = Settings()