# app/main.py
from dotenv import load_dotenv
from pathlib import Path

# 优先加载 .env（确保路径正确）
load_dotenv(Path(__file__).parent.parent / ".env")

# app/main.py
from fastapi import FastAPI
from app.api import routes as api_routes # 导入我们的路由
from app.core.config import settings # 导入配置
import os
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth as auth_routes

# 在应用启动前，确保 Llama Cloud API Key 被设置到环境变量中
os.environ['LLAMA_CLOUD_API_KEY'] = settings.LLAMA_CLOUD_API_KEY

app = FastAPI(title="Grant Application Extractor API")

# 2. 定义允许的源
origins = [
    "https://grant-extractor-frontend.onrender.com",
    "http://localhost:49570", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 只能写具体域名
    allow_credentials=True,     # 登录/上传时需要 cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

# 将 api_routes 中定义的所有路由包含到主应用中
app.include_router(api_routes.router, prefix="/api/v1")
app.include_router(auth_routes.router, prefix="/api/v1/auth")

@app.get("/")
def read_root():
    return {"message": "欢迎使用 Grant Extractor API", "docs_url": "/docs"}

# uvicorn app.main:app --reload
#在浏览器中打开 http://127.0.0.1:8000，你应该能看到欢迎信息。
#打开 http://127.0.0.1:8000/docs，你会看到FastAPI自动生成的交互式API文档。
#在文档页面，你可以直接上传一个PDF文件来测试 /api/v1/extract/ 端点，非常方便！
#生成 requirements.txt
#当你的项目能正常工作后，创建一个依赖列表，方便其他人或部署时安装。
#pip freeze > requirements.txt
