import os
import logging
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from exam_analyzer import ExamAnalyzer
from rag_analyzer import RAGAnalyzer

# --- 1. SETUP AND CONFIGURATION ---

# Load environment variables from .env file FIRST
load_dotenv()

# Configure logging once
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app object
app = Flask(__name__)
CORS(app)

# Get configuration from environment variables
PDF_FOLDER = os.getenv('PDF_FOLDER', './pdf_files')
CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
DATA_FOLDER = os.getenv('DATA_FOLDER', './exam_data')


# --- 2. GLOBAL VARIABLES & INITIALIZATION FUNCTIONS ---
# These functions will be called by run_server.py

exam_analyzer = None
rag_analyzer = None


def initialize_exam_analyzer():
    """Initializes the main exam data analyzer."""
    global exam_analyzer
    try:
        logger.info("Initializing ExamAnalyzer...")
        exam_analyzer = ExamAnalyzer()
        if not os.path.exists(DATA_FOLDER):
            logger.warning(f"Data folder {DATA_FOLDER} not found. Analyzer will have no data.")
            return False

        exam_analyzer.load_json_files(DATA_FOLDER)
        exam_analyzer.build_embeddings()
        logger.info("✅ ExamAnalyzer initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize ExamAnalyzer: {e}", exc_info=True)
        return False


def initialize_rag_analyzer():
    """Initializes the RAG document analyzer."""
    global rag_analyzer
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY not found in .env file. RAG tool will be disabled.")
        return False

    os.environ["GOOGLE_API_KEY"] = gemini_api_key

    try:
        logger.info("Initializing RAGAnalyzer...")
        rag_analyzer = RAGAnalyzer(
            pdf_folder=PDF_FOLDER,
            persist_directory=CHROMA_PERSIST_DIR
        )
        rag_analyzer.load_or_create_vectorstore()
        logger.info("✅ RAGAnalyzer initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAGAnalyzer: {e}", exc_info=True)
        return False


# --- 3. API ENDPOINTS ---

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the status of all systems."""
    return jsonify({
        'server_status': 'healthy',
        'exam_analyzer_ready': exam_analyzer is not None and exam_analyzer.is_fitted,
        'rag_analyzer_ready': rag_analyzer is not None and rag_analyzer.qa_chain is not None
    })

@app.route('/topics-for-course', methods=['GET'])
def get_topics_for_course():
    """
    GET /topics-for-course - Get all predefined topics for a specific course code.

    Query parameters:
    - code: string (required) - The course code to search for (e.g., "CST206").

    Returns:
    {
        "courseCode": "CST206",
        "topics": [...]
    }
    or an error object.
    """
    course_code = request.args.get('code')
    if not course_code:
        return jsonify({'error': 'Query parameter "code" is required.'}), 400

    try:
        # Construct the correct path to the JSON file from the 'engine' directory
        # __file__ is the path to the current file (app.py)
        # os.path.dirname(__file__) is the directory of the current file ('.../PassPilot/engine')
        # os.path.join(..., '..') moves one directory up to '.../PassPilot'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '..', 'exams_info.json')

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Find the course matching the code (case-insensitive search)
        for course in data.get('courses', []):
            if course.get('courseCode', '').upper() == course_code.upper():
                logger.info(f"Found topics for course code: {course_code}")
                return jsonify({
                    "courseCode": course.get('courseCode'),
                    "topics": course.get('topics', [])
                })

        # If the loop finishes without finding the course
        logger.warning(f"Course code '{course_code}' not found in exams_info.json")
        return jsonify({'error': f"Course with code '{course_code}' not found."}), 404

    except FileNotFoundError:
        logger.error(f"Critical error: exams_info.json not found at path: {json_path}")
        return jsonify({'error': 'Server configuration file not found.'}), 500
    except Exception as e:
        logger.error(f"Error fetching topics for course: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# == RAG Endpoints ==

@app.route('/ask', methods=['POST'])
def ask_document():
    """Asks a question to the RAG system about the indexed PDFs."""
    if not rag_analyzer or not rag_analyzer.qa_chain:
        return jsonify({'error': 'RAG system not ready. Check server startup logs.'}), 503

    data = request.get_json()
    if not data or not data.get('query') or not data['query'].strip():
        return jsonify({'error': 'Missing or empty required field: query'}), 400

    answer = rag_analyzer.ask(data['query'])
    return jsonify({'query': data['query'], 'answer': answer})


@app.route('/re-index', methods=['POST'])
def re_index_documents():
    """Manually triggers the re-indexing of all PDFs."""
    if not rag_analyzer:
        return jsonify({'error': 'RAG system not initialized.'}), 503

    logger.info("Manual re-indexing process triggered via API.")
    rag_analyzer.index_documents()
    return jsonify({'status': 'success', 'message': 'Re-indexing process completed.'})


# == Exam Analyzer Endpoints ==

@app.route('/query', methods=['POST'])
def semantic_query():
    """Perform semantic search on exam questions."""
    if not exam_analyzer or not exam_analyzer.is_fitted:
        return jsonify({'error': 'Exam analyzer not ready.'}), 503

    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({'error': 'Missing required field: query'}), 400

    query = data['query'].strip()
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400

    similarity_threshold = data.get('similarity_threshold', 0.5)
    top_k = data.get('top_k', 20)

    results = exam_analyzer.semantic_search(query, similarity_threshold, top_k)
    return jsonify({
        'query': query,
        'total_matches': len(results),
        'results': results,
        'module_distribution': exam_analyzer.get_module_distribution(results),
        'marks_distribution': exam_analyzer.get_marks_distribution(results)
    })


@app.route('/pass-strategy', methods=['POST'])
def pass_strategy():
    """Generates a targeted study plan to pass an exam."""
    if not exam_analyzer or not exam_analyzer.is_fitted:
        return jsonify({'error': 'Exam analyzer not ready.'}), 503

    data = request.get_json()
    if not data: return jsonify({'error': 'Invalid JSON payload'}), 400

    studied_topics = data.get('studied_topics', [])
    internal_marks = data.get('internal_marks', 0)
    external_pass_threshold = data.get('external_pass_threshold', 40)
    overall_pass_threshold = data.get('overall_pass_threshold', 75)

    marks_needed_for_overall = overall_pass_threshold - internal_marks
    target_external_marks = max(external_pass_threshold, marks_needed_for_overall)

    strategy = exam_analyzer.get_pass_strategy(studied_topics, target_external_marks)
    strategy['inputs'] = { 'internal_marks': internal_marks, 'studied_topics': studied_topics, 'calculated_target_marks': target_external_marks }
    return jsonify(strategy)


@app.route('/pass-simulation', methods=['POST'])
def pass_simulation():
    """Runs a Monte Carlo simulation for pass probability."""
    if not exam_analyzer or not exam_analyzer.is_fitted:
        return jsonify({'error': 'Exam analyzer not ready.'}), 503

    data = request.get_json()
    if not data: return jsonify({'error': 'Invalid JSON payload'}), 400

    studied_topics = data.get('studied_topics', [])
    internal_marks = data.get('internal_marks', 0)
    external_pass_threshold = data.get('external_pass_threshold', 40)
    overall_pass_threshold = data.get('overall_pass_threshold', 75)
    
    marks_needed_for_overall = overall_pass_threshold - internal_marks
    target_external_marks = max(external_pass_threshold, marks_needed_for_overall)
    
    simulation_results = exam_analyzer.run_pass_simulation(studied_topics, target_external_marks)
    simulation_results['inputs'] = { 'internal_marks': internal_marks, 'studied_topics': studied_topics, 'calculated_target_marks': target_external_marks }
    return jsonify(simulation_results)


@app.route('/topics', methods=['GET'])
def analyze_topics():
    """Get an analysis of pre-labeled topics from the exam data."""
    if not exam_analyzer or not exam_analyzer.is_fitted:
        return jsonify({'error': 'Exam analyzer not ready.'}), 503

    min_frequency = int(request.args.get('min_frequency', 2))
    topic_list = exam_analyzer.get_topic_analysis(min_frequency)
    return jsonify({
        'total_topics': len(topic_list),
        'parameters': {'min_frequency': min_frequency},
        'topics': topic_list
    })


@app.route('/stats', methods=['GET'])
def dataset_stats():
    """Get general statistics about the loaded dataset."""
    if not exam_analyzer or not exam_analyzer.is_fitted:
        return jsonify({'error': 'Exam analyzer not ready.'}), 503

    return jsonify(exam_analyzer.get_stats())


# --- 4. ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with a list of available endpoints."""
    available_endpoints = [rule.rule for rule in app.url_map.iter_rules() if 'static' not in rule.endpoint]
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': sorted(list(set(available_endpoints)))
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle unexpected 500 errors."""
    logger.error(f"Internal Server Error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred.'}), 500

# NOTE: The if __name__ == '__main__': block is intentionally removed.
# The server is now started exclusively by run_server.py.