# app/services/extractor_service.py
import os
import uuid
from llama_cloud_services import LlamaExtract
from llama_cloud import ExtractConfig
from app.models.schemas import Application

# --- Agent 初始化 ---
print("正在初始化 Llama Cloud Extractor...")
_extractor = LlamaExtract()

# --- 这里是关键的修改：使用高质量的 System Prompt ---
_extract_config = ExtractConfig(
    extraction_mode="FAST",
    system_prompt='''You are a highly capable AI assistant specializing in information extraction, designed to help grant reviewers quickly understand the key points of an application.
Your task is to carefully read the provided application text and extract the required information.
You MUST format your response as a JSON object that strictly adheres to the 'Application' schema. Do not add any extra text, explanations, or apologies before or after the JSON.
If a specific piece of information cannot be found in the text, use null for that field. Do not invent or infer data.''',
    extraction_target="PER_DOC",
    use_reasoning=True,
    cite_sources=False # 根据你的需求设置
)

# 使用 "获取或创建" 逻辑
agent_name = "grant-application-parser-api-main"
_agent = None
try:
    print(f"正在尝试获取或创建代理: '{agent_name}'...")
    existing_agents = _extractor.list_agents()
    for existing_agent in existing_agents:
        if existing_agent.name == agent_name:
            # 检查配置是否匹配，如果不匹配，可能需要删除重建
            # 为简单起见，我们先直接复用
            _agent = existing_agent
            print(f"✅ 成功复用已存在的代理: '{agent_name}'")
            break
    if _agent is None:
        print(f"⚠️ 未找到代理，正在创建新的代理: '{agent_name}'")
        _agent = _extractor.create_agent(
            name=agent_name,
            data_schema=Application,
            config=_extract_config # 使用我们新的、高质量的配置
        )
        print(f"✅ 成功创建新代理: '{agent_name}'")
except Exception as e:
    print(f"❌ 初始化 Agent 失败: {e}")
    raise RuntimeError(f"无法初始化 Llama Cloud Agent: {e}")

print("✅ Agent 初始化流程完成！")


async def extract_data_from_file(file) -> Application:
    """
    Receives an uploaded file object, saves it temporarily, calls Llama Cloud,
    validates the result into a Pydantic model, and returns the extracted data.
    """
    if not _agent:
        # If the agent failed to initialize on startup, raise an error.
        raise RuntimeError("Llama Cloud Agent is not initialized and cannot process requests.")

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")

    try:
        # Save the uploaded file to a temporary location
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Core Llama Cloud call
        print(f"Service Layer: Starting extraction from file '{file.filename}'...")
        result = _agent.extract(temp_file_path)
        print("Service Layer: Extraction complete.")

        # --- Robustly get the raw data from the result ---
        raw_extracted_data = None
        if result and result.data:
            if isinstance(result.data, list):
                if result.data:
                    raw_extracted_data = result.data[0]
            else:
                raw_extracted_data = result.data

        # If no data was extracted at all, return None
        if not raw_extracted_data:
            print("Warning: Llama Cloud processed the file but returned no data.")
            return None

        # --- Key Fix: Validate the raw dictionary into a Pydantic model instance ---
        try:
            print("Service Layer: Validating and converting extracted dict into a Pydantic model...")
            application_instance = Application.model_validate(raw_extracted_data)

            # --- Post-processing logic on the Pydantic instance ---
            # Example: Ensure workspace is also listed as a partner
            if application_instance.workspace:
                if application_instance.partners is None:
                    application_instance.partners = []
                if application_instance.workspace not in application_instance.partners:
                    print(f"Post-processing: Adding workspace '{application_instance.workspace}' to partners list.")
                    application_instance.partners.append(application_instance.workspace)

            # Return the validated and processed Pydantic model instance
            return application_instance

        except Exception as e:
            # This will catch errors if the data returned from Llama Cloud
            # does not match the Application schema.
            print(f"❌ Error while validating the extracted data into a Pydantic model: {e}")
            return None

    finally:
        # Ensure the temporary file is always deleted
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)