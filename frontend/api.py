
import requests
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractorClient:
    """
    Client for interacting with the PDF Extractor Backend API.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Initializes the client with the backend base URL.
        """
        self.base_url = base_url.rstrip("/")

    def extract_data(self, file_name: str, file_data: bytes, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Sends a file to the backend for data extraction.

        Args:
            file_name (str): The name of the file.
            file_data (bytes): The binary content of the file.
            mime_type (str): The MIME type of the file.

        Returns:
            Dict[str, Any]: The extracted JSON data.

        Raises:
            ConnectionError: If the backend is unreachable.
            ValueError: If the backend returns an error.
        """
        url = f"{self.base_url}/extract"
        files = {"file": (file_name, file_data, mime_type)}
        
        try:
            logger.info(f"Sending file '{file_name}' to {url}...")
            response = requests.post(url, files=files, timeout=300) # Increased timeout to 5 minutes
            
            if response.status_code == 200:
                logger.info("Extraction successful.")
                return response.json()
            
            else:
                error_msg = f"Backend Error ({response.status_code}): {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to backend.")
            raise ConnectionError("Could not connect to the backend server. Please ensure the backend is running.")
        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            raise ConnectionError("The request to the backend timed out.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")
