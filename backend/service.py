
import os
import io
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqProcessor:
    """
    Handles PDF data extraction using pdfplumber (text extraction)
    and Groq's LLM API (structured JSON generation).
    """

    def __init__(self):
        """
        Validates that the GROQ_API_KEY is present at startup.
        """
        load_dotenv(override=True)
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY not found in environment variables")
        logger.info("GroqProcessor initialized successfully.")

    def _get_client(self) -> Groq:
        """
        Returns a fresh Groq client using the latest key from .env.
        Calling load_dotenv(override=True) ensures key changes in .env
        take effect without restarting the server.
        """
        load_dotenv(override=True)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return Groq(api_key=api_key)

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extracts all text from a PDF using pdfplumber.

        Args:
            pdf_content (bytes): Raw PDF bytes.

        Returns:
            str: All extracted text joined by newlines.
        """
        text_parts = []
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def extract_data_from_pdf(self, pdf_content: bytes, prompt_text: str = None) -> str:
        """
        Extracts structured JSON data from a PDF using Groq LLM.

        Args:
            pdf_content (bytes): The raw bytes of the PDF file.
            prompt_text (str): Optional custom prompt.

        Returns:
            str: The extracted JSON string.
        """
        default_prompt = """
You are a highly accurate data extraction agent.
Your task is to extract all the information from the provided document text into a structured JSON format.

Rules:
1. Identify all fields in the form (labels and values).
2. Use a detailed nested structure for sections (e.g., "Personal Information", "Education").
3. Represent checkboxes as booleans (true/false) or string values if applicable.
4. Handle tables by creating lists of objects.
5. If a field is empty, represent it as null or an empty string.
6. Return ONLY the JSON string. Do not include markdown formatting (like ```json ... ```) or explanations.
"""

        final_prompt = prompt_text if prompt_text else default_prompt

        try:
            logger.info("Extracting text from PDF...")
            pdf_text = self._extract_text_from_pdf(pdf_content)

            if not pdf_text.strip():
                raise RuntimeError("No text could be extracted from the PDF. It may be a scanned image-only PDF.")

            logger.info(f"Extracted {len(pdf_text)} characters from PDF. Sending to Groq...")

            client = self._get_client()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": final_prompt},
                    {"role": "user", "content": f"Here is the form content to extract:\n\n{pdf_text}"}
                ],
                temperature=0.0,
                max_tokens=4096,
            )

            result = response.choices[0].message.content
            logger.info("Received response from Groq API.")
            return result

        except Exception as e:
            logger.error(f"Error during Groq API call: {e}")
            raise RuntimeError(f"Error processing document with Groq: {str(e)}")
