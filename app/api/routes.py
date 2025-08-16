# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import extractor_service, generation_service
from app.models.schemas import FullAnalysisResponse

router = APIRouter()

@router.post("/extract/", response_model=FullAnalysisResponse)
async def handle_full_analysis(file: UploadFile = File(...)):
    """
    Receives a PDF, extracts structured data, generates a synopsis and keywords, and returns the full analysis.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    pdf_content_bytes = await file.read()
    # 重置文件指针，以便 extractor_service 也能读取
    await file.seek(0)

    try:
        # Step 1: 提取 (传递文件对象)
        extracted_data = await extractor_service.extract_data_from_file(file)
        if not extracted_data:
            raise HTTPException(status_code=404, detail="Could not extract structured data.")

        # Step 2: 生成摘要 (传递JSON和PDF字节流)
        synopsis_text = await generation_service.generate_synopsis(extracted_data, pdf_content_bytes)

        # Step 3: 生成关键词 (只传递JSON)
        keywords_list = await generation_service.generate_keywords(synopsis_text, extracted_data)

        # Step 3: Combine into the final response
        final_response = FullAnalysisResponse(
            extracted_data=extracted_data,
            synopsis=synopsis_text,
            keywords=keywords_list
        )
        return final_response

    except Exception as e:
        import traceback
        traceback.print_exc() # Print full error for debugging
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")