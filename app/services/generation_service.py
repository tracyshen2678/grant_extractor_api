import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.schemas import Application
from typing import List
import fitz  # PyMuPDF

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def get_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """从PDF的字节流中提取纯文本。"""
    text = ""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from PDF bytes: {e}")
    return text

# 修改 generate_synopsis 函数的签名，让它接收 pdf_bytes
async def generate_synopsis(application_data: Application, pdf_bytes: bytes) -> str:
    """
    使用混合上下文（JSON + 原文）生成一个忠实于关键细节的摘要。
    """
    application_json = application_data.model_dump_json(indent=2)
    full_text = get_text_from_pdf_bytes(pdf_bytes)

    system_prompt = """You are an expert grant application analyst. Your task is to write a 3-4 sentence synopsis in Swedish.
You will be given structured JSON data and the full original text.
Your synopsis MUST be grounded in the facts from the JSON, but you MUST cross-reference the original text to find and include the specific, crucial details mentioned in the user's instructions.
"""

    human_prompt = f"""Here is the structured data for fact-checking:
--- JSON DATA ---
{application_json}
--- END JSON DATA ---

Here is the full original text to find specific details:
--- ORIGINAL TEXT ---
{full_text}
--- END ORIGINAL TEXT ---

Now, construct the synopsis by following these strict rules:
1.  **Sentence 1 and Sentence 2(Ambition & Method):** Start with the applicant's main goal. You MUST find and include specific theme and technical details from the original text.
2.  **Sentence 3 (Outcome & Impact):** Describe the final artistic product. **Crucially, if the data mentions features related to social impact, such as accessibility for impaired individuals or broad community inclusion, weave this information into the description of the outcome.** This is a key feature when present.
3.  **Sentence 4 (Legacy & Sharing):** Describe the project's community impact and plans for knowledge sharing. Include these two aspects if they are present in the data:
    *   **Community Engagement:** Detail any specific outreach activities.
    *   **Knowledge Sharing:** Mention any plans for creating lasting resources that share the project's methods.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": human_prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating synopsis: {e}"

async def generate_keywords(synopsis_text: str, application_data: Application) -> List[str]:
    """
    根据结构化数据生成具有通用性的概念关键词。
    """
    application_json = application_data.model_dump_json(indent=2)
    system_prompt = """You are an AI specializing in data tagging. Based ONLY on the provided Swedish summary text and the original structured data, generate a list of 8-10 relevant keywords in Swedish. Your task is to **conceptualize and summarize**, not just extract phrases. These keywords should represent the project's underlying themes and values.
You MUST respond with ONLY a JSON object formatted as {"keywords": ["keyword1", "keyword2", ...]}.
"""

    human_prompt = f"""Here is the summary text:\n"{synopsis_text}

Now, generate conceptual keywords by analyzing the data through these universal lenses. For each lens, generate 1-3 keywords if applicable:
1.  **"Domain & Core Focus"**: Keywords describing **WHAT** the project is fundamentally about. This includes the main field or domain (e.g., 'Art', 'Science', 'History'), the primary subject matter, the format of the output and its scale.
2.  **Social Dimension"**: Keywords related to community engagement, target audience, **diversity**, **inclusion**, or **accessibility**.
3.  **Method & Engagement (Metod & Engagemang):** What is the overall approach to involving the community?
4.  **Knowledge & Legacy (Kunskap & Arv):** Does it involve creation/research process,knowledge sharing or long-term impact.

Based on this analytical framework, generate the list of conceptual keywords in Swedish.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": human_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3, # 稍微增加一点温度，鼓励它进行概念关联
        )

        raw_response_content = response.choices[0].message.content
        print(f"--- DEBUG: Raw Keyword JSON from AI ---\n{raw_response_content}\n------------------------------------")
        keyword_data = json.loads(raw_response_content)

        if "keywords" in keyword_data and isinstance(keyword_data["keywords"], list):
            return keyword_data["keywords"]
        elif isinstance(keyword_data, dict) and len(keyword_data) == 1:
            first_value = next(iter(keyword_data.values()))
            if isinstance(first_value, list):
                print("Warning: Keywords found under an unexpected key.")
                return first_value

        return ["Error: Could not find a valid list of keywords in the response."]

    except Exception as e:
        print(f"Error generating or parsing keywords: {e}")
        import traceback
        traceback.print_exc()
        return [f"Error during keyword generation: {e}"]