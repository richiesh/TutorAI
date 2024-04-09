import PyPDF2


class TextReader:
    """
    A class for reading text from PDF files.

    Attributes:
        pages (list): A list to store text content extracted from each page of the PDF.
        bookname (str): Name of the PDF file being read.
    """

    def __init__(self) -> None:
        """
        Initializes the TextReader object with empty lists for pages and an empty string for bookname.
        """
        self.pages = []
        self.book_name = ""

    def __str__(self) -> str:
        """
        Returns a string representation of the TextReader object.

        Returns:
            str: A string containing the bookname followed by the text from all pages.
        """
        return f"{self.book_name}({' '.join(self.pages)})"

    def read(self, pdf_file):
        """
        Reads text from the given PDF file.

        Args:
            pdf_file (str): The path to the PDF file.

        Raises:
            FileNotFoundError: If the specified PDF file does not exist.

        Notes:
            This method extracts text from each page of the PDF file and stores it in the 'pages' list.
            It also extracts the name of the PDF file (without the .pdf extension) and stores it in 'bookname'.
        """
        # Open the PDF file
        with open(pdf_file, "rb") as f:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(f)

            self.pages = []

            # Iterate through each page of the PDF
            for page_num in range(len(pdf_reader.pages)):
                # Get the text from the current page
                page = pdf_reader.pages[page_num]
                self.pages.append(page.extract_text())
            self.book_name = pdf_file[: pdf_file.find(".pdf")]

    def read_page(self, pdf_file, page_num):
        with open(pdf_file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            return text
