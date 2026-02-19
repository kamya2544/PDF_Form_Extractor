
import json
import uvicorn
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from service import GroqProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Form Extractor API")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the processor globally
try:
    processor = GroqProcessor()
except Exception as e:
    logger.critical(f"Failed to start application due to processor initialization error: {e}")
    processor = None

@app.get("/")
def home():
    """Health check endpoint."""
    return {"message": "PDF Extractor API is running"}

@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Endpoint to process uploaded PDF and return extracted JSON.
    """
    if not processor:
        raise HTTPException(status_code=503, detail="Service not initialized properly")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")
    
    try:
        logger.info(f"Processing file: {file.filename}")
        content = await file.read()
        
        # Call the processor
        json_result_str = processor.extract_data_from_pdf(content)
        
        # Clean up the markdown code blocks if Gemini ignores the "no markdown" rule
        clean_json_str = json_result_str.strip()
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-3]
            
        try:
            parsed_json = json.loads(clean_json_str)
            return parsed_json
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from model output. Returning raw output wrapped in error object.")
            # If parsing fails, return the raw text wrapping it in a structure
            return {"error": "Failed to parse JSON from model output", "raw_output": json_result_str}
            
    except RuntimeError as re:
        # Handle known errors from the service
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in /extract endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
