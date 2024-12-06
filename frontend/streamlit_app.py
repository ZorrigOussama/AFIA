import streamlit as st
import requests
from PIL import Image


# Configure page settings
st.set_page_config(
    page_title="Ocean Information Assistant",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main-header {
        font-size: 2.5em;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1em;
    }
    .sub-header {
        font-size: 1.5em;
        color: #0D47A1;
        margin-bottom: 0.5em;
    }
    .info-text {
        font-size: 1.1em;
        color: #424242;
    }
    </style>
""", unsafe_allow_html=True)

# Set the API base URL
API_BASE_URL = "http://localhost:5000"

# Main title with custom styling
st.markdown("<h1 class='main-header'>🌊 Ocean Information Assistant</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### About")
    st.info(
        """
        This application helps you learn about oceans and marine life through:
        * Text-based queries about ocean-related topics
        * Image analysis of marine photographs
        * Bilingual support (English/French)
        """
    )
    st.markdown("### Usage Tips")
    st.warning(
        """
        * For text queries, be specific in your questions
        * For images, ensure they are ocean-related
        * Questions can be asked in English or French
        """
    )

# Create tabs for different query types
tab1, tab2 = st.tabs(["📝 Text Query", "🖼️ Image Query"])

with tab1:
    st.markdown("<h2 class='sub-header'>Text Query</h2>", unsafe_allow_html=True)

    # Text input for queries with placeholder
    text_query = st.text_input(
        "Enter your question about oceans:",
        placeholder="Example: What are coral reefs? / Exemple: Qu'est-ce que les récifs coralliens?",
        key="text_query"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_button = st.button("🔍 Submit Query", use_container_width=True)

    if submit_button and text_query:
        with st.spinner('Processing your query...'):
            try:
                # Make API request
                response = requests.post(
                    f"{API_BASE_URL}/query/text",
                    json={"query": text_query}
                )

                if response.status_code == 200:
                    result = response.json()

                    # Display response in a nice format
                    st.markdown("### 📄 Answer:")
                    st.markdown(f">{result['response']}")

                    # Display sources if available
                    if result.get('sources') and result['sources'] != ["No specific source found"]:
                        st.markdown("### 📚 Sources:")
                        for source in result['sources']:
                            st.markdown(f"- {source}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    elif submit_button:
        st.warning("Please enter a question.")

with tab2:
    st.markdown("<h2 class='sub-header'>Image Query</h2>", unsafe_allow_html=True)

    # Image upload section
    uploaded_file = st.file_uploader(
        "Upload an ocean-related image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image related to oceans, marine life, or marine environments"
    )

    # Optional query text for the image
    image_query = st.text_input(
        "Enter your question about the image (optional):",
        placeholder="What can you tell me about this image? / Que pouvez-vous me dire sur cette image?",
        key="image_query"
    )

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_button = st.button("🔍 Analyze Image", use_container_width=True)

        if analyze_button:
            with st.spinner('Analyzing image...'):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)

                    # Prepare the files and data for the request
                    files = {
                        'image': ('image.jpg', uploaded_file, 'image/jpeg')
                    }
                    data = {
                        'query': image_query if image_query else "What can you tell me about this image?"
                    }

                    # Make API request
                    response = requests.post(
                        f"{API_BASE_URL}/query/image",
                        files=files,
                        data=data
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.markdown("### 📝 Analysis:")
                        st.markdown(f">{result['response']}")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        "<p style='text-align: center; color: #666666;'>Made with ❤️ for Ocean Conservation</p>",
        unsafe_allow_html=True
    )
