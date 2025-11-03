"""
FastAPI-based lightweight REST API for PDF translation
Author: Claude Code
Date: 2025
"""

import io
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pdf2zh import translate_stream

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDFMathTranslate API",
    description="Lightweight REST API for translating scientific PDF documents while preserving formulas and layouts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response models
class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    version: str = Field(..., example="1.0.0")
    service: str = Field(..., example="PDFMathTranslate API")


class ErrorResponse(BaseModel):
    error: str = Field(..., example="Translation failed")
    detail: Optional[str] = Field(None, example="Unsupported language code")


class ServicesResponse(BaseModel):
    services: list = Field(
        ...,
        example=[
            "google", "bing", "deepl", "deeplx", "ollama", "openai",
            "azure-openai", "gemini", "zhipu", "silicon", "groq"
        ]
    )


# Supported translation services
SUPPORTED_SERVICES = [
    "google", "bing", "deepl", "deeplx", "deepseek",
    "ollama", "openai", "azure-openai", "gemini",
    "zhipu", "silicon", "groq", "grok", "moonshot",
    "qwen", "tencent", "azure", "dify", "anythingllm",
    "modelscope", "xinference", "anthropic", "argos"
]

# Supported languages
SUPPORTED_LANGUAGES = [
    "zh", "en", "ja", "ko", "es", "fr", "de", "ru",
    "pt", "it", "ar", "hi", "th", "vi", "id", "tr"
]


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="PDFMathTranslate API"
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="PDFMathTranslate API"
    )


@app.get("/services", response_model=ServicesResponse, tags=["Info"])
async def list_services():
    """List all supported translation services"""
    return ServicesResponse(services=SUPPORTED_SERVICES)


@app.get("/languages", tags=["Info"])
async def list_languages():
    """List all supported languages"""
    return {
        "languages": SUPPORTED_LANGUAGES,
        "note": "Use ISO 639-1 language codes (e.g., 'en' for English, 'zh' for Chinese)"
    }


@app.post("/translate/mono", tags=["Translation"])
async def translate_mono(
    file: UploadFile = File(..., description="PDF file to translate"),
    lang_in: str = Form("en", description="Source language code (e.g., 'en')"),
    lang_out: str = Form("zh", description="Target language code (e.g., 'zh')"),
    service: str = Form("google", description="Translation service to use"),
    model: Optional[str] = Form(None, description="Model name (for LLM services)"),
    thread: int = Form(4, description="Number of threads for translation", ge=1, le=16),
    callback: Optional[str] = Form(None, description="Custom prompt callback")
):
    """
    Translate PDF and return monolingual version (original text replaced with translation)

    **Parameters:**
    - **file**: PDF file to upload
    - **lang_in**: Source language (default: en)
    - **lang_out**: Target language (default: zh)
    - **service**: Translation service (default: google)
    - **model**: Model name for LLM services (optional)
    - **thread**: Number of threads (default: 4, max: 16)
    - **callback**: Custom prompt template (optional)

    **Returns:**
    - Translated PDF file (monolingual version)
    """
    try:
        logger.info(f"Received translation request: {file.filename}, {lang_in}->{lang_out}, service={service}")

        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Validate languages
        if lang_in not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported source language: {lang_in}")
        if lang_out not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {lang_out}")

        # Validate service
        service_base = service.split(':')[0].lower()
        if service_base not in SUPPORTED_SERVICES:
            raise HTTPException(status_code=400, detail=f"Unsupported translation service: {service}")

        # Read PDF file
        pdf_bytes = await file.read()

        # Prepare translation parameters
        translate_params = {
            'lang_in': lang_in,
            'lang_out': lang_out,
            'service': service,
            'thread': thread,
        }

        if model:
            translate_params['model'] = model
        if callback:
            translate_params['callback'] = callback

        # Translate
        logger.info(f"Starting translation with params: {translate_params}")
        stream_mono, stream_dual = translate_stream(
            stream=pdf_bytes,
            **translate_params
        )

        # Return monolingual PDF
        output_filename = file.filename.replace('.pdf', f'-{lang_out}.pdf')

        return StreamingResponse(
            io.BytesIO(stream_mono),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{output_filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/translate/dual", tags=["Translation"])
async def translate_dual(
    file: UploadFile = File(..., description="PDF file to translate"),
    lang_in: str = Form("en", description="Source language code (e.g., 'en')"),
    lang_out: str = Form("zh", description="Target language code (e.g., 'zh')"),
    service: str = Form("google", description="Translation service to use"),
    model: Optional[str] = Form(None, description="Model name (for LLM services)"),
    thread: int = Form(4, description="Number of threads for translation", ge=1, le=16),
    callback: Optional[str] = Form(None, description="Custom prompt callback")
):
    """
    Translate PDF and return bilingual version (original text + translation)

    **Parameters:**
    - **file**: PDF file to upload
    - **lang_in**: Source language (default: en)
    - **lang_out**: Target language (default: zh)
    - **service**: Translation service (default: google)
    - **model**: Model name for LLM services (optional)
    - **thread**: Number of threads (default: 4, max: 16)
    - **callback**: Custom prompt template (optional)

    **Returns:**
    - Translated PDF file (bilingual version)
    """
    try:
        logger.info(f"Received bilingual translation request: {file.filename}, {lang_in}->{lang_out}, service={service}")

        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Validate languages
        if lang_in not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported source language: {lang_in}")
        if lang_out not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {lang_out}")

        # Validate service
        service_base = service.split(':')[0].lower()
        if service_base not in SUPPORTED_SERVICES:
            raise HTTPException(status_code=400, detail=f"Unsupported translation service: {service}")

        # Read PDF file
        pdf_bytes = await file.read()

        # Prepare translation parameters
        translate_params = {
            'lang_in': lang_in,
            'lang_out': lang_out,
            'service': service,
            'thread': thread,
        }

        if model:
            translate_params['model'] = model
        if callback:
            translate_params['callback'] = callback

        # Translate
        logger.info(f"Starting bilingual translation with params: {translate_params}")
        stream_mono, stream_dual = translate_stream(
            stream=pdf_bytes,
            **translate_params
        )

        # Return dual PDF
        output_filename = file.filename.replace('.pdf', f'-dual-{lang_out}.pdf')

        return StreamingResponse(
            io.BytesIO(stream_dual),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{output_filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bilingual translation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/translate", tags=["Translation"])
async def translate_both(
    file: UploadFile = File(..., description="PDF file to translate"),
    lang_in: str = Form("en", description="Source language code (e.g., 'en')"),
    lang_out: str = Form("zh", description="Target language code (e.g., 'zh')"),
    service: str = Form("google", description="Translation service to use"),
    model: Optional[str] = Form(None, description="Model name (for LLM services)"),
    thread: int = Form(4, description="Number of threads for translation", ge=1, le=16),
    callback: Optional[str] = Form(None, description="Custom prompt callback")
):
    """
    Translate PDF and return both monolingual and bilingual download links

    **Parameters:**
    - **file**: PDF file to upload
    - **lang_in**: Source language (default: en)
    - **lang_out**: Target language (default: zh)
    - **service**: Translation service (default: google)
    - **model**: Model name for LLM services (optional)
    - **thread**: Number of threads (default: 4, max: 16)
    - **callback**: Custom prompt template (optional)

    **Returns:**
    - JSON with base64-encoded PDFs or download instructions
    """
    try:
        logger.info(f"Received full translation request: {file.filename}, {lang_in}->{lang_out}, service={service}")

        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Validate languages
        if lang_in not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported source language: {lang_in}")
        if lang_out not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {lang_out}")

        # Validate service
        service_base = service.split(':')[0].lower()
        if service_base not in SUPPORTED_SERVICES:
            raise HTTPException(status_code=400, detail=f"Unsupported translation service: {service}")

        # Read PDF file
        pdf_bytes = await file.read()

        # Prepare translation parameters
        translate_params = {
            'lang_in': lang_in,
            'lang_out': lang_out,
            'service': service,
            'thread': thread,
        }

        if model:
            translate_params['model'] = model
        if callback:
            translate_params['callback'] = callback

        # Translate
        logger.info(f"Starting full translation with params: {translate_params}")
        stream_mono, stream_dual = translate_stream(
            stream=pdf_bytes,
            **translate_params
        )

        # Return JSON response with information
        import base64
        return JSONResponse({
            "status": "success",
            "message": "Translation completed successfully",
            "original_filename": file.filename,
            "mono_filename": file.filename.replace('.pdf', f'-{lang_out}.pdf'),
            "dual_filename": file.filename.replace('.pdf', f'-dual-{lang_out}.pdf'),
            "mono_size_bytes": len(stream_mono),
            "dual_size_bytes": len(stream_dual),
            "mono_base64": base64.b64encode(stream_mono).decode('utf-8'),
            "dual_base64": base64.b64encode(stream_dual).decode('utf-8'),
            "note": "Use /translate/mono or /translate/dual endpoints to download PDF directly"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


def create_app() -> FastAPI:
    """Factory function to create FastAPI app"""
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
