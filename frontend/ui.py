
import streamlit as st
import json
import logging
from api import PDFExtractorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractorUI:
    """
    Class to manage the Streamlit User Interface for the PDF Extractor.
    """
    
    def __init__(self):
        """
        Initialize the UI components and API client.
        """
        self.client = PDFExtractorClient()
        self.setup_page()

    def setup_page(self):
        """
        Configures the Streamlit page settings.
        """
        st.set_page_config(
            page_title="PDF Form Extractor",
            page_icon="📄",
            layout="wide"
        )

    def render_header(self):
        """
        Renders the application header.
        """
        st.title("📄 PDF Form Extractor")
        st.markdown(
            """
            Upload a PDF form (e.g., Admission Form, Invoice) to extract structured data 
            using **Google Gemini 1.5 Flash**.
            """
        )

    def render_uploader(self):
        """
        Renders the file uploader and handles the extraction process.
        """
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        
        if uploaded_file is not None:
            st.info(f"File '{uploaded_file.name}' uploaded successfully.")
            
            if st.button("Extract Data", type="primary"):
                self.process_file(uploaded_file)

    def process_file(self, uploaded_file):
        """
        Process the uploaded file by sending it to the backend.
        """
        with st.spinner("Analyzing document... This may take a moment."):
            try:
                # Reset pointer to start just in case
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                
                # Call the API Client
                data = self.client.extract_data(
                    file_name=uploaded_file.name,
                    file_data=file_bytes
                )
                
                self.display_results(data)
                
            except ConnectionError as ce:
                st.error(f"Connection Error: {str(ce)}")
            except ValueError as ve:
                st.error(f"Processing Error: {str(ve)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                logger.exception("Unexpected error in UI processing.")

    def display_results(self, data: dict):
        """
        Displays the extracted data and download options.
        """
        st.success("Extraction Complete!")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📝 Extracted Data")
            st.json(data, expanded=True)
        
        with col2:
            st.subheader("💾 Download")
            json_str = json.dumps(data, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="extracted_data.json",
                mime="application/json",
                help="Click to save the extracted data as a JSON file."
            )

    def run(self):
        """
        Main method to run the application.
        """
        self.render_header()
        self.render_uploader()
        self.render_footer()

    def render_footer(self):
        """
        Renders the application footer.
        """
        st.markdown("---")
        st.caption("Powered by **FastAPI** & **Google Gemini**")

if __name__ == "__main__":
    try:
        app = PDFExtractorUI()
        app.run()
    except Exception as e:
        st.error(f"Application failed to start: {e}")
