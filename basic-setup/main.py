from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from retrieval_pipeline import AgriRAGSystem
from image_analysis import AgriImageAnalyzer
from typing import Optional
import uvicorn
import base64
import io
from PIL import Image
import logging
import time

# Initialize FastAPI app
app = FastAPI(
    title="AgriSearch Bot API",
    description="Agriculture & Forestry Intelligence Assistant",
    version="1.0.0"
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agri")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = AgriRAGSystem(persist_directory="chroma_db")
image_analyzer = AgriImageAnalyzer()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    image: Optional[str] = None  # Base64 encoded image string

class ChatResponse(BaseModel):
    response: str
    richContent: Optional[dict] = None
    sources: list = []

@app.get("/")
async def root():
    return {
        "message": "AgriSearch Bot API is running",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AgriSearch Bot is running"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user query and return AI response with rich content.
    If image is provided, context from image analysis is added to the query.
    """
    try:
        user_query = request.message
        logger.info("/chat request received: message_len=%d, image_present=%s", len(user_query or ""), bool(request.image))
        
        # Handle Image Analysis if image is present
        if request.image:
            try:
                logger.info("Image present in request — starting decode and analysis")
                # Decode base64 image
                # Remove header if present (e.g., "data:image/jpeg;base64,")
                if "," in request.image:
                    header, encoded = request.image.split(",", 1)
                else:
                    encoded = request.image
                image_data = base64.b64decode(encoded)
                pil_image = Image.open(io.BytesIO(image_data))

                logger.debug("Image decoded successfully; size=(%s, %s)", getattr(pil_image, 'width', '?'), getattr(pil_image, 'height', '?'))

                # Analyze image
                start_img = time.time()
                analysis_result = image_analyzer.analyze_image(pil_image)
                img_duration = time.time() - start_img
                logger.info("Image analysis completed in %.3fs", img_duration)
                logger.debug("Image analysis result: %s", analysis_result)

                # Enhance query with image context
                user_query = f"{user_query}\n\n[Image Context: {analysis_result}]"
                
            except Exception as img_error:
                logger.exception("Image processing error")
                # Continue with just text query if image fails, but append note
                user_query = f"{user_query}\n\n[Note: Image analysis failed: {str(img_error)}]"

        logger.info("Sending query to RAG system (len=%d)", len(user_query or ""))
        start = time.time()
        result = rag_system.process_query(user_query)
        duration = time.time() - start
        logger.info("RAG processing finished in %.3fs", duration)
        logger.debug("RAG result keys: %s", list(result.keys()))
        
        logger.info("Responding to client; richContent=%s sources_count=%d", bool(result.get("richContent")), len(result.get("sources", [])))
        return ChatResponse(
            response=result["response"],
            richContent=result.get("richContent"),
            sources=result.get("sources", [])
        )
    
    except Exception as e:
        logger.exception("Unhandled error while processing /chat request")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# This allows running with: python main.py
if __name__ == "__main__":
    logger.info("Starting uvicorn server for AgriSearch Bot API")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)