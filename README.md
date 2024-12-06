```markdown
# Ocean Information Assistant 🌊

## Overview
The Ocean Information Assistant is an interactive application that provides information about oceans, marine life, and marine conservation through both text-based queries and image analysis. It supports bilingual interactions (English and French) and uses advanced AI models to provide accurate and relevant information.

## Features
- 🔍 Text-based queries about "nuit de l'info" topic
- 🖼️ Image analysis of marine photographs
- 🌐 Bilingual support (English/French)
- 📚 Source attribution for responses
- 🤖 Powered by GPT-4o
- 💻 User-friendly web interface

## Project Structure
```
AFIA/
│
├── backend/
│   ├── data/           # Directory containing ocean-related documents
│   ├── main.py        # Flask API server
│   └── requirements.txt
│
├── frontend/
│   ├── streamlit_app.py    # Streamlit web interface
│   └── requirements.txt
│
└── README.md
```

## Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Internet connection

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ocean_assistant.git
cd ocean_assistant
```

2. **Set up virtual environment (recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd ../frontend
pip install -r requirements.txt
```

5. **Environment Setup**
Create a `.env` file in the backend directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Data Setup
1. A data directory has been created in the backend folder to store sample data.
2. You can add your ocean-related documents (PDF, TXT, etc.) to this directory.


## Running the Application

1. **Start the Backend Server**
```bash
# From the project root directory
cd backend
python main.py
```
The Flask server will start on `http://localhost:5000`

2. **Start the Frontend Application**
Open a new terminal window and run:
```bash
# From the project root directory
cd frontend
streamlit run streamlit_app.py
```
The Streamlit interface will automatically open in your default web browser at `http://localhost:8501`

## Usage Instructions

### Text Queries
1. Navigate to the "Text Query" tab
2. Enter your question about oceans in English or French
3. Click "Submit Query"
4. View the response and any relevant sources

### Image Analysis
1. Navigate to the "Image Query" tab
2. Upload an ocean-related image
3. (Optional) Enter a specific question about the image
4. Click "Analyze Image"
5. View the detailed analysis of the image

## Troubleshooting

### Common Issues and Solutions

1. **API Key Error**
```
Error: OpenAI API key not found
```
Solution: Ensure your `.env` file exists and contains a valid API key

2. **Backend Connection Error**
```
Cannot connect to backend server
```
Solution: 
- Verify the Flask server is running
- Check if port 5000 is available
- Ensure no firewall is blocking the connection

3. **Image Upload Issues**
```
Error: File too large
```
Solution: Ensure your image is less than 10MB and in a supported format (jpg, png, jpeg)

## API Documentation

### Text Query Endpoint
- **URL**: `/query/text`
- **Method**: POST
- **Body**:
```json
{
    "query": "Your question here"
}
```

### Image Query Endpoint
- **URL**: `/query/image`
- **Method**: POST
- **Form Data**:
  - `image`: Image file
  - `query`: Optional query text

## Dependencies

### Backend
- Flask
- llama-index
- chromadb
- python-dotenv
- langdetect
- openai
- flask-cors

### Frontend
- streamlit
- requests
- Pillow

```
