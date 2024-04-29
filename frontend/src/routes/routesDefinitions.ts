const baseAPIUrl: string = "http://localhost:8000/api";

const apiRoutes = {
  createFlashcards: `${baseAPIUrl}/create-flashcards/`,
  login: `${baseAPIUrl}/login/`,
  signup: `${baseAPIUrl}/create-user/`,
  search: `${baseAPIUrl}/search/`,
  fileupload: `${baseAPIUrl}/store-curriculum/`,
  quiz: `${baseAPIUrl}/quiz/`,
  gradeQuizAnswer: `${baseAPIUrl}/graded-quiz/`,
  fileUpload: `${baseAPIUrl}/store-curriculum/`,
  createCompendium: `${baseAPIUrl}/compendium/`,
};

export default apiRoutes;
