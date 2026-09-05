
import pytest

from multilingual.translation.translator import (
    EnglishHindiTranslator,
    DemoTranslationProvider
)


# ------------------------------------------------------------
# Mock glossary for testing
# ------------------------------------------------------------

class MockGlossary:

    TERMS = [
        {
            "matched_text": "Patent",
            "term_id": "PAT-001",
            "category": "Patent",
            "preferred_hi": "पेटेंट"
        },
        {
            "matched_text": "Prior Art",
            "term_id": "PAT-002",
            "category": "Patent",
            "preferred_hi": "पूर्व कला"
        },
        {
            "matched_text": "Ayurveda",
            "term_id": "AYU-001",
            "category": "Ayurveda",
            "preferred_hi": "आयुर्वेद"
        },
        {
            "matched_text": "Traditional Knowledge",
            "term_id": "TK-001",
            "category": "Traditional Knowledge",
            "preferred_hi": "पारंपरिक ज्ञान"
        },
        {
            "matched_text": "Agricultural Knowledge",
            "term_id": "AGR-001",
            "category": "Agriculture",
            "preferred_hi": "कृषि ज्ञान"
        }
    ]

    def find_terms(self, text):

        results = []

        for term in self.TERMS:

            if term["matched_text"].lower() in text.lower():
                results.append(term)

        return results


# ------------------------------------------------------------
# Fixture
# ------------------------------------------------------------

@pytest.fixture
def translator():

    glossary = MockGlossary()
    provider = DemoTranslationProvider()

    return EnglishHindiTranslator(
        glossary_engine=glossary,
        provider=provider
    )


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

def test_patent_term_detection(translator):

    result = translator.translate(
        "This is a patent."
    )

    assert result["detected_terms"][0]["term_id"] == "PAT-001"


def test_patent_translation(translator):

    result = translator.translate(
        "This is a patent"
    )

    assert "पेटेंट" in result["final_translation"]


def test_traditional_knowledge_detection(translator):

    result = translator.translate(
        "Traditional Knowledge is important."
    )

    ids = [
        term["term_id"]
        for term in result["detected_terms"]
    ]

    assert "TK-001" in ids


def test_ayurveda_detection(translator):

    result = translator.translate(
        "Ayurveda uses traditional knowledge."
    )

    ids = [
        term["term_id"]
        for term in result["detected_terms"]
    ]

    assert "AYU-001" in ids


def test_empty_input(translator):

    with pytest.raises(ValueError):

        translator.translate("")


def test_non_string_input(translator):

    with pytest.raises(TypeError):

        translator.translate(123)


def test_validation(translator):

    result = translator.translate(
        "This is a patent"
    )

    assert result["validation"]["valid"] is True


def test_case_insensitive_detection(translator):

    result = translator.translate(
        "THIS IS A PATENT"
    )

    ids = [
        term["term_id"]
        for term in result["detected_terms"]
    ]

    assert "PAT-001" in ids

