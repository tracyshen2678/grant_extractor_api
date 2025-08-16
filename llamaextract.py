import os
from getpass import getpass
from typing import List, Optional
from pydantic import BaseModel, Field
import json # 引入 json 模块以便更好地打印结果

# --- 1. 设置 API Key ---
# 检查环境变量中是否有API Key，如果没有，则提示用户输入
if not os.getenv("LLAMA_CLOUD_API_KEY"):
    os.environ['LLAMA_CLOUD_API_KEY'] = getpass("Add your LlamaCloud API Key: ")

# --- 2. 引入 Llama Cloud 相关库 ---
# 注意：你的原始代码里引入了两次 pydantic 和 Field，这里整理一下
try:
    from llama_cloud_services import LlamaExtract
    from llama_cloud import ExtractConfig
except ImportError:
    print("错误: 'llama_cloud_services' 或 'llama_cloud' 未安装。")
    print("请运行: pip install llama-cloud-services llama-cloud")
    exit()

# --- 3. 定义 Pydantic Schema ---
# (这部分你的代码是完整的，我直接复制过来)
class CoFunding(BaseModel):
    """Details about co-funding from other sources."""
    is_mentioned: bool = Field(description="Is co-funding from other sources mentioned?")
    amount: Optional[float] = Field(default=None, description="The amount of co-funding, if specified.")
    status: Optional[str] = Field(default=None, description="The status of the co-funding, e.g., 'Confirmed' or 'Sought'.")

class SupportingDocument(BaseModel):
    """Checklist for attached supporting documents."""
    cv_attached: bool = Field(description="Is a CV or resume attached?")
    portfolio_provided: bool = Field(description="Is a portfolio or a link to one provided?")
    letters_of_intent_attached: bool = Field(description="Are any Letters of Intent from partners attached?")
    partner_agreements_attached: bool = Field(description="Are any formal agreements with partners attached?")

class Application(BaseModel):
    # 1. Basic Formalities
    applicant_name: Optional[str] = Field(default=None, description="The full name of the individual or organization applying.")
    applicant_type: Optional[str] = Field(default=None, description="The type of applicant, e.g., 'Individual' or 'Organization'.")
    requested_amount: Optional[float] = Field(default=None, description="The total amount of funding requested in the application's currency.")
    project_duration: Optional[str] = Field(default=None, description="The total duration of the project, e.g., '24 months' or '1 year'.")
    project_start_date: Optional[str] = Field(default=None, description="The proposed start date of the project (as a string to capture formats like 'Summer 2025').")
    project_end_date: Optional[str] = Field(default=None, description="The proposed end date of the project.")
    main_artistic_field: Optional[str] = Field(default=None, description="The primary artistic discipline of the project, e.g., 'Visual Arts', 'Music', 'Literature'.")
    main_goal_or_output: Optional[str] = Field(default=None, description="A concise description of the project's main goal or final deliverable, e.g., 'A bronze triptych'.")
    location: Optional[str] = Field(default=None, description="The primary physical location(s) where the project will take place or be exhibited.")
    target_audience: Optional[str] = Field(default=None, description="A description of the primary group of people the project aims to reach or serve.")
    community_engagement_methods: Optional[List[str]] = Field(default=None, description="A list of methods for public interaction, e.g., 'Workshops', 'Public casting events'.")
    detailed_budget_provided: bool = Field(description="Indicates whether a detailed cost breakdown is included in the application.")
    co_funding: Optional[CoFunding] = Field(default=None, description="Details regarding co-funding from other sources.")
    partners: Optional[List[str]] = Field(default=None, description="A list of named partners or collaborating organizations mentioned in the application.")
    risk_analysis_provided: bool = Field(description="Indicates whether a risk analysis with mitigation strategies is included.")
    workspace: Optional[str] = Field(default=None, description="The specified workshop, studio, or space where the artistic creation will take place.")
    supporting_documents: Optional[SupportingDocument] = Field(default=None, description="A checklist of provided supporting documents.")

# --- 4. 配置和创建提取 Agent ---
# (这部分你的代码也是完整的，我做了一点小的格式调整)

# Initialize client
extractor = LlamaExtract()

extract_config = ExtractConfig(
    extraction_mode="FAST", # FAST, BALANCED, MULTIMODAL, PREMIUM
    system_prompt='''You are a highly capable AI assistant specializing in information extraction, designed to help grant reviewers quickly understand the key points of an application.
Your task is to carefully read the provided application text and extract the required information.
You MUST format your response as a JSON object that strictly adheres to the `Application` schema. Do not add any extra text, explanations, or apologies before or after the JSON.
If a specific piece of information cannot be found in the text, use `null` for that field. Do not invent or infer data.''',
    extraction_target="PER_DOC", # PER_DOC, PER_PAGE
    use_reasoning=True,
    cite_sources=False
)

# Create extraction agent
# 建议给 agent 起一个唯一的、描述性的名字
agent = extractor.create_agent(name="grant-application-parser-v5", data_schema=Application, config=extract_config)


# --- 5. 实际执行提取并处理结果 (这是你缺少的关键部分) ---

# 定义你要提取的文件名
file_to_extract = "Ansokan.pdf" # 确保这个文件和你的python脚本在同一个目录下

print(f"🚀 开始从文件 '{file_to_extract}' 中提取信息...")

try:
    # 核心调用：执行提取
    result = agent.extract(file_to_extract)

    print("✅ 提取完成！")

    # --- 这里是最终版的、最稳健的结果处理逻辑 ---

    extracted_application = None

    if result and result.data:
        # 检查 result.data 是列表还是单个对象
        if isinstance(result.data, list):
            # 如果是列表，检查它是否为空
            if result.data:
                extracted_application = result.data[0]
        else:
            # 如果不是列表，就假设它本身就是那个对象
            extracted_application = result.data

    # 现在检查我们是否成功获取到了 application 对象
    if extracted_application:
        print("\n--- 提取结果 ---")
        # 确保 extracted_application 是 Pydantic 模型实例，然后美观地打印
        if hasattr(extracted_application, 'model_dump_json'):
            print(extracted_application.model_dump_json(indent=2))
        else:
            # 如果不是，就普通打印
            import json
            print(json.dumps(extracted_application, indent=2))

        # 你也可以安全地访问字段
        print("\n--- 快速概览 ---")
        # 使用 getattr 来安全访问，防止对象没有这个属性
        print(f"申请人: {getattr(extracted_application, 'applicant_name', 'N/A')}")
        print(f"申请金额: {getattr(extracted_application, 'requested_amount', 'N/A')}")
        print(f"项目目标: {getattr(extracted_application, 'main_goal_or_output', 'N/A')}")

    else:
        # 如果经过所有检查，还是没能获取到对象，就打印警告
        print("⚠️ 警告: Llama Cloud 成功处理了文件，但未能从中解析出有效数据。")
        print(f"原始返回内容: {result}") # 打印原始返回，方便调试

except FileNotFoundError:
    print(f"❌ 错误: 文件 '{file_to_extract}' 未找到。")
except Exception as e:
    print(f"❌ 提取过程中发生未知错误: {e}")
    # 打印错误的 traceback，获得更详细的信息
    import traceback
    traceback.print_exc()