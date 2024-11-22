import spacy

class PDFTriggerDetector:
    def __init__(self):
        """
        Initialize the NLP model and keywords for detecting PDF triggers.
        """
        # Load spaCy's English NLP model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define base keywords and their synonyms
        self.base_keywords = {
            "document": ["doc", "file", "attachment", "paperwork"],
            "proof": ["evidence", "verification"],
            "contract": ["agreement", "deal"],
            "send": ["deliver", "provide", "attach"]
        }
        
        # Expand keywords with synonyms
        self.expanded_keywords = self.expand_keywords(self.base_keywords)

    def expand_keywords(self, base_keywords):
        """
        Expand the base keywords with synonyms using spaCy's semantic similarity.
        """
        expanded = set()
        for base_word, synonyms in base_keywords.items():
            # Add the base word and its synonyms
            expanded.add(base_word)
            expanded.update(synonyms)
        return expanded

    def analyze_email(self, email_body):
        """
        Analyze the email body to determine if a PDF should be sent.

        Args:
            email_body (str): The text content of the email.

        Returns:
            bool: True if the PDF should be sent, False otherwise.
        """
        doc = self.nlp(email_body.lower())

        # Check if any token matches the expanded keyword set
        for token in doc:
            if token.lemma_ in self.expanded_keywords:
                return True  # Trigger PDF sending if a match is found

        return False  # No match found
