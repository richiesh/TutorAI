from django.urls import path


from .views import health_check
from flashcards.views import (
    create_compendium,
    create_flashcards,
    create_quiz,
    generate_mock_flashcard,
    create_rag_response,
    post_curriculum,
)

urlpatterns = [
    # path("create-user/", register_user, name="create-user"),
    # path("login/", login, name="login"),
    path("health-check/", health_check, name="Health_check"),
    path("store-curriculum/", post_curriculum, name="store-curriculum"),
    path("create-flashcards/", create_flashcards, name="create-flashcards"),
    path(
        "generate-mock-flashcard/",
        generate_mock_flashcard,
        name="generate-mock-flashcard",
    ),
    path("search/", create_rag_response, name="create-rag-response"),
    path("quiz/", create_quiz, name="create-quiz"),
    path("compendium/", create_compendium, name="create-compendium"),
]
