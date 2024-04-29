""" The service module contains the business logic of the application. """

from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.files.uploadedfile import InMemoryUploadedFile

from flashcards.knowledge_base.response_formulation import (
    create_question_answer_pair,
    grade_question_answer_pair,
    response_formulation,
)
from flashcards.rag_service import get_context, get_page_range, post_context
from flashcards.text_to_flashcards import generate_flashcards, OpenAIFlashcardGenerator
from flashcards.text_scraper.text_extractor import TextExtractor
from flashcards.learning_resources import (
    Compendium,
    GradedQuiz,
    Page,
    Flashcard,
    QuestionAnswer,
    Quiz,
    RagAnswer,
)


def process_flashcards(document_name: str, start: int, end: int) -> list[Flashcard]:
    """
    Generate flashcards for a specific page range and file
    """
    print("[INFO] Trying to find relevant document", flush=True)
    pages = get_page_range(document_name, start, end)
    flashcards: list[Flashcard] = []
    print("[INFO] Generating flashcards", flush=True)

    # Use ThreadPoolExecutor to parallelize the API calls
    with ThreadPoolExecutor() as executor:
        # Schedule the execution of each page processing and hold the future objects
        futures = [executor.submit(_process_page, page) for page in pages]

        # As each future completes, gather the results
        for future in as_completed(futures):
            flashcards.extend(future.result())

    return flashcards


def _process_page(page: str) -> list[Flashcard]:
    flashcards_from_page = generate_flashcards(page)
    post_context(page.text, page.page_num, page.pdf_name)
    return flashcards_from_page


def store_curriculum(uploaded_file: InMemoryUploadedFile) -> bool:
    """
    Process the file and store the pages as curriculum in a database.
    """
    print("[INFO] Processing file", flush=True)

    # Extract text from the uploaded file

    extractor = TextExtractor()
    pages: list[Page] = extractor.extractData(uploaded_file)

    for page in pages:
        print(f"[INFO] Processing page {page.page_num}", flush=True)
        # Save content
        context_posted: bool = post_context(page.text, page.page_num, page.pdf_name)
        # TODO: HANDLE FAILURE CASE OF POST CONTEXT
    return context_posted


def request_flashcards_by_page_range(
    pdf_name: str, page_num_start: int, page_num_end
) -> list[Flashcard]:
    """
    Request flashcards for a specific page range and pdf from the database
    """
    # Get the flashcards from the database
    pages: list[Page] = get_page_range(pdf_name, page_num_start, page_num_end)
    flashcards: list[Flashcard] = []
    for page in pages:
        flashcards_from_page = generate_flashcards(page)
        flashcards.extend(flashcards_from_page)

    return flashcards


def process_answer(
    documents: list[str], user_question: str, chat_history: list[dict[str, str]]
) -> RagAnswer:

    # Get a list of relevant contexts from the database
    curriculum = []
    for document_name in documents:
        curriculum.extend(get_context(document_name, user_question))

    # Use this list to generate a response
    answer_GPT = response_formulation(user_question, curriculum, chat_history)

    answer = RagAnswer(answer_GPT, curriculum)
    return answer


def generate_quiz(
    document: str, start: int, end: int, learning_goals: str = []
) -> Quiz:
    """
    Generates a quiz for the document
    """
    print(f"[INFO] Generating quiz for document {document}", flush=True)
    if start > end:
        raise ValueError(
            "The start index of the document can not be after then the end index!"
        )

    learning_goals = """Knowledge. The student has knowledge about basic concepts within complex function theory. The student knows about Fourier series and the use of these in the study of partial differential equations. The student knows basic theory of partial differential equations. The student has a solid foundation for further studies of complex analysis and differential equations. The student has knowledge of the requirements for stringency in mathematical analysis.
Skills. The student has basic technical computational skills that are important in complex analysis and differential equations. The student can understand mathematical reasoning that combines different concepts and results from the course content. The student is able to derive simple results that are based on the academic content of the course."""

    # Generate the quiz
    questions: list[QuestionAnswer] = []

    pages: list[Page] = get_page_range(document, start, end)
    for page in pages:
        new_questions = create_question_answer_pair(page.text, [learning_goals])
        questions.extend(new_questions)

    return Quiz(document, start, end, questions)


def grade_quiz(
    questions: str, correct_answers: str, student_answers: list[str]
) -> GradedQuiz:
    """
    Grade the quiz based on the student answers
    """
    questionAnswerPairs = [
        QuestionAnswer(question, correct_answer)
        for question, correct_answer in zip(questions, correct_answers)
    ]

    graded_quiz = GradedQuiz([])
    for questionAnswerPair, student_answer in zip(questionAnswerPairs, student_answers):
        feedback = grade_question_answer_pair(questionAnswerPair, student_answer)
        graded_quiz.graded_questions.append(feedback)
    return graded_quiz

def generate_compendium_template(text: str) -> tuple[str, str]:
    """
    Generate a compendium template for the text
    """

    key_concepts_format = "France: A large country in westeren Europe | Java Virtual Machine: A microarchitecture that the Java programming language uses | Deforestation: The process in which a forest is destroyed by humans"
    key_concepts_template = f"Generate a list of key concepts from the given text{text}. Use only the most important concepts. Do not include any unnecessary information. Use only the information that is in the text. Use the following format: {key_concepts_format}"

    summary_template = f"Generate a summary of the given text{text}. Use only the most important information. Do not include any unnecessary information. Use only the information that is in the text."

    return key_concepts_template, summary_template

def generate_compendium(document: str, start: int, end: int) -> Compendium:
    """
    Generates a compendium for the document
    """

    # Retrieve the pages from the database
    context_pages: list[Page] = get_page_range(document, start, end)
    print(f"[INFO] Generating compendium for document {document}", flush=True)
    # Generate the compendium
    summaries = []
    key_concepts = []

    for page in context_pages:
        # Extract the key concepts and summaries from the page
        # Append the key concepts and summaries to the lists
        print(f"[INFO] Generating compendium for page {page.page_num}", flush=True)
        concept_template, summary_template = generate_compendium_template(page.text)
        concept = OpenAIFlashcardGenerator.request_chat_completion("system", message=concept_template)
        summary = OpenAIFlashcardGenerator.request_chat_completion("system", message=summary_template)
        print(f"[INFO] Generated key concepts and summary for page {concept}", flush=True)
        key_concepts.append(concept)
        summaries.append(summary)

    # Definitions of Terms

    # Equations and Formulas if any

    # Create pages with the content
    pages = []

    compendium = Compendium(document, start, end, pages)
    return key_concepts
