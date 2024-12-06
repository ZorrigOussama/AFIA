from flask import Flask, request, jsonify
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb
import os
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
from langdetect import detect
import base64
from openai import OpenAI as DirectOpenAI
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Create client and collection
chroma_client = chromadb.EphemeralClient()
chroma_collection = chroma_client.create_collection("Oceans")

# Load documents from the Dataset directory
documents = SimpleDirectoryReader("backend/data").load_data()

# Set up ChromaVectorStore and load data
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

# Define query templates for both languages
qa_tmpl_str_en = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Instructions:\n"
    "1. The response must be in English.\n"
    "2. If the query is not related to the context, respond EXACTLY with: 'Sorry, I only have information about the theme of 'Nuit de l'info.'\n"
    "3. If the query is related, provide a response using ONLY the information from the context.\n"
    "Query: {query_str}\n"
    "Response (in English): "
)

qa_tmpl_str_fr = (
    "Informations contextuelles ci-dessous.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Instructions:\n"
    "1. La réponse doit être en français.\n"
    "2. Si la question n'est pas liée au contexte, répondre EXACTEMENT: 'Désolé, je n'ai pas d'information sur ce sujet.'\n"
    "3. Si la question est liée, fournir une réponse en utilisant UNIQUEMENT les informations du contexte.\n"
    "Question: {query_str}\n"
    "Réponse (en français): "
)

qa_tmpl_en = PromptTemplate(qa_tmpl_str_en)
qa_tmpl_fr = PromptTemplate(qa_tmpl_str_fr)

def create_language_specific_query(query_text, detected_lang):
    """Create a language-specific query instruction"""
    if detected_lang == 'fr':
        return (
            f"Instructions: Translate the following context to French and answer in French.\n"
            f"Query: {query_text}\n"
            f"Provide a detailed answer IN FRENCH based on the context."
        )
    return query_text

def get_query_engine(language):
    """Create query engine based on language"""
    template = qa_tmpl_fr if language == 'fr' else qa_tmpl_en

    llm = OpenAI(model="gpt-4o", temperature=0.3)

    return index.as_query_engine(
        text_qa_template=template,
        similarity_top_k=2,
        response_mode="tree_summarize",
        llm=llm
    )

def check_response_relevance(response, similarity_threshold=0.7):
    if not hasattr(response, 'source_nodes') or not response.source_nodes:
        return False
    return any(node.score >= similarity_threshold for node in response.source_nodes if hasattr(node, 'score'))

# Image analysis function
def analyze_image(image_data, query_text, language):
    try:
        client = DirectOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # First, check if the image is ocean-related
        validation_prompt = ("You are an expert in oceanography. First, determine if this image is related to "
                           "oceans, marine life, marine environments, or marine conservation. "
                           "Respond with ONLY 'YES' if it is related, or 'NO' if it is not.")

        validation_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": validation_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10
        )

        is_ocean_related = validation_response.choices[0].message.content.strip().upper() == "YES"

        # If not ocean-related, return appropriate message based on language
        if not is_ocean_related:
            if language == 'fr':
                return "Désolé, je ne peux analyser que les images liées aux océans, à la vie marine ou à l'environnement marin."
            else:
                return "Désolé, votre image n'est pas en rapport avec le thème de la Nuit de l'info."

        # If ocean-related, proceed with detailed analysis
        if language == 'fr':
            system_prompt = (
                "Vous êtes un expert en océanographie. Analysez cette image liée aux océans et "
                "fournissez une réponse détaillée en français qui:\n"
                "1. Identifie les éléments marins présents\n"
                "2. Explique leur importance dans l'écosystème marin\n"
                "3. Mentionne tout aspect lié à la conservation ou aux défis environnementaux si pertinent"
            )
        else:
            system_prompt = (
                "You are an expert in oceanography. Analyze this ocean-related image and "
                "provide a detailed response in English that:\n"
                "1. Identifies the marine elements present\n"
                "2. Explains their importance in the marine ecosystem\n"
                "3. Mentions any conservation or environmental challenges if relevant"
            )

        analysis_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        return analysis_response.choices[0].message.content

    except Exception as e:
        return f"Error analyzing image: {str(e)}"
# Text-only query endpoint
@app.route('/query/text', methods=['POST'])
def process_text_query():
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400

        query_text = data['query']

        # Detect language
        try:
            language = detect(query_text)
            language = 'fr' if language == 'fr' else 'en'
        except:
            language = 'en'

        # Create language-specific query
        modified_query = create_language_specific_query(query_text, language)

        # Get appropriate query engine for the language
        query_engine = get_query_engine(language)
        response = query_engine.query(modified_query)

        # Get appropriate "not found" message
        not_found_msg = "Désolé, je n'ai pas d'information sur ce sujet." if language == 'fr' else "Sorry, I don't have information on that topic."

        if not check_response_relevance(response):
            return jsonify({
                'response': not_found_msg,
                'sources': ["No relevant sources found"]
            })

        # Extract sources
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                if hasattr(node, 'metadata') and 'file_name' in node.metadata:
                    sources.append(node.metadata['file_name'])

        return jsonify({
            'response': str(response),
            'sources': list(set(sources)) if sources else ["No specific source found"]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Image query endpoint
@app.route('/query/image', methods=['POST'])
def process_image_query():
    try:
        # Check if the request contains a file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        query = request.form.get('query', 'What can you tell me about this image?')

        # Validate file type
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400

        # Read and encode the image
        image_data = base64.b64encode(file.read()).decode('utf-8')

        # Detect language from query
        try:
            language = detect(query)
            language = 'fr' if language == 'fr' else 'en'
        except:
            language = 'en'

        # Analyze the image
        analysis = analyze_image(image_data, query, language)


        return jsonify({
            'response': analysis,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
