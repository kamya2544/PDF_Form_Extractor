
# Structured PDF Form Extractor

This project uses Google Gemini 1.5 Flash to extract structured JSON data from PDF forms.

## Architecture
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **AI**: Gemini 1.5 Flash

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r backend/requirements.txt
    pip install -r frontend/requirements.txt
    ```

2.  **Configure API Key**
    - Open `.env` file.
    - Add your Google Gemini API Key: `GOOGLE_API_KEY=your_key_here`

3.  **Run the Backend**
    Open a terminal and run:
    ```bash
    cd backend
    uvicorn main:app --reload
    ```
    The API will run at `http://127.0.0.1:8000`.

4.  **Run the Frontend**
    Open a *new* terminal and run:
    ```bash
    cd frontend
    streamlit run ui.py
    ```
    The UI will open in your browser.

## Usage
1.  Upload a PDF form (e.g., Admission Form).
2.  Click "Extract Data".
3.  View and download the extracted JSON.
