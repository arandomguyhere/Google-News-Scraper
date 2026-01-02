"""NLP processor for entity extraction and text analysis."""

import logging
from typing import List, Dict, Any, Set
from collections import Counter
import re

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Processes stories for entity extraction and text analysis."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.entity_types = config.get('entity_types', ['PERSON', 'ORG', 'GPE', 'LOC'])
        self.nlp = None
        self._initialize_spacy()

    def _initialize_spacy(self):
        """Initialize spaCy NLP model."""
        try:
            import spacy
            try:
                self.nlp = spacy.load('en_core_web_sm')
                logger.info("Loaded spaCy model: en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
                logger.info("Falling back to basic processing")
                self.nlp = None
        except ImportError:
            logger.warning("spaCy not installed. Using basic processing.")
            self.nlp = None

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        if not text:
            return {}

        if self.nlp:
            return self._extract_entities_spacy(text)
        else:
            return self._extract_entities_basic(text)

    def _extract_entities_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy."""
        doc = self.nlp(text[:1000000])  # Limit text length

        entities = {}
        for ent in doc.ents:
            if ent.label_ in self.entity_types:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)

        # Deduplicate while preserving order
        for label in entities:
            seen = set()
            unique = []
            for entity in entities[label]:
                if entity.lower() not in seen:
                    seen.add(entity.lower())
                    unique.append(entity)
            entities[label] = unique

        return entities

    def _extract_entities_basic(self, text: str) -> Dict[str, List[str]]:
        """Basic entity extraction without spaCy (fallback)."""
        # Very basic pattern matching for demonstration
        entities = {}

        # Extract capitalized words as potential entities
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

        # Common first names and org keywords
        org_keywords = ['Corp', 'Inc', 'Ltd', 'LLC', 'Company', 'Group', 'Agency', 'Ministry', 'Department']

        potential_orgs = []
        potential_persons = []

        for word in words:
            if any(kw in word for kw in org_keywords):
                potential_orgs.append(word)
            elif len(word.split()) <= 3:  # Names are usually 1-3 words
                potential_persons.append(word)

        if potential_orgs:
            entities['ORG'] = list(set(potential_orgs))[:10]
        if potential_persons:
            entities['PERSON'] = list(set(potential_persons))[:10]

        return entities

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract important keywords from text."""
        if not text:
            return []

        # Remove common stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'said',
            'say', 'says'
        }

        # Tokenize and filter
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        filtered_words = [w for w in words if w not in stopwords]

        # Count frequencies
        word_freq = Counter(filtered_words)
        keywords = [word for word, _ in word_freq.most_common(top_n)]

        return keywords

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using TF-IDF cosine similarity."""
        if not text1 or not text2:
            return 0.0

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )

            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return float(similarity)

        except Exception as e:
            logger.warning(f"Error calculating similarity: {e}")
            # Fallback to simple word overlap
            return self._simple_similarity(text1, text2)

    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Simple word overlap similarity (fallback)."""
        words1 = set(re.findall(r'\b[a-z]{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b[a-z]{3,}\b', text2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def process_story(self, story) -> Dict[str, Any]:
        """Process a story and extract all NLP features."""
        # Combine title and description for analysis
        text = f"{story.title} {story.description} {story.content}"

        entities = self.extract_entities(text)
        keywords = self.extract_keywords(text)

        return {
            'story_id': story.id,
            'entities': entities,
            'keywords': keywords,
            'text_for_similarity': text
        }
