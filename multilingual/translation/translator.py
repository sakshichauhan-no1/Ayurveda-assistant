from abc import ABC, abstractmethod
import re
from typing import Any, Dict, List


from multilingual.glossary.glossary_anchor import (
    load_glossary,
    find_terms
)


# ============================================================
# 1. TRANSLATION PROVIDER INTERFACE
# ============================================================

class TranslationProvider(ABC):
    """
    Base interface for any English → Hindi translation provider.

    Later this can be replaced with:
    - Google Translate
    - DeepL
    - OpenAI
    - Gemini
    - Hugging Face
    - Local translation model
    """

    @abstractmethod
    def translate(
        self,
        text: str,
        source: str = "en",
        target: str = "hi"
    ) -> str:
        """
        Translate text from source language to target language.
        """
        raise NotImplementedError


# ============================================================
# 2. DEMO TRANSLATION PROVIDER
# ============================================================

class DemoTranslationProvider(TranslationProvider):
    """
    Simple translation provider for development and testing.

    This is NOT a real machine translation model.

    It demonstrates how the translation pipeline behaves
    before connecting a real translation service.
    """

    DEMO_TRANSLATIONS = {
        "this is a patent":
            "यह एक पेटेंट है",

        "patent protection is important":
            "पेटेंट संरक्षण महत्वपूर्ण है",

        "traditional knowledge is important":
            "पारंपरिक ज्ञान महत्वपूर्ण है",

        "ayurveda uses traditional knowledge":
            "आयुर्वेद पारंपरिक ज्ञान का उपयोग करता है",
    }

    def translate(
        self,
        text: str,
        source: str = "en",
        target: str = "hi"
    ) -> str:
        """
        Translate demo text while preserving glossary
        placeholders such as __TERM_0__, __TERM_1__, etc.
        """

        normalized = text.strip().lower()

        # ----------------------------------------------------
        # Direct translation
        # ----------------------------------------------------

        if normalized in self.DEMO_TRANSLATIONS:
            return self.DEMO_TRANSLATIONS[normalized]

        # ----------------------------------------------------
        # Protected glossary terms
        # ----------------------------------------------------
        #
        # Example:
        #
        # "This is a __TERM_0__"
        #
        # becomes:
        #
        # "यह एक __TERM_0__ है"
        #
        # The placeholder is deliberately preserved.
        # restore_terms() will replace it later with the
        # preferred Hindi glossary term.
        # ----------------------------------------------------

        placeholder_pattern = r"__TERM_\d+__"

        if re.search(
            placeholder_pattern,
            text,
            flags=re.IGNORECASE
        ):

            # This handles:
            #
            # This is a __TERM_0__
            #
            match = re.fullmatch(
                r"\s*this\s+is\s+a\s+(__TERM_\d+__)\s*",
                text,
                flags=re.IGNORECASE
            )

            if match:
                placeholder = match.group(1)
                return f"यह एक {placeholder} है"

            # This handles:
            #
            # __TERM_0__ is important
            #
            match = re.fullmatch(
                r"\s*(__TERM_\d+__)\s+is\s+important\s*",
                text,
                flags=re.IGNORECASE
            )

            if match:
                placeholder = match.group(1)
                return f"{placeholder} महत्वपूर्ण है"

            # This handles:
            #
            # This is __TERM_0__
            #
            match = re.fullmatch(
                r"\s*this\s+is\s+(__TERM_\d+__)\s*",
                text,
                flags=re.IGNORECASE
            )

            if match:
                placeholder = match.group(1)
                return f"यह {placeholder} है"

            # This handles:
            #
            # __TERM_0__ uses __TERM_1__
            #
            match = re.fullmatch(
                r"\s*(__TERM_\d+__)\s+uses\s+(__TERM_\d+__)\s*",
                text,
                flags=re.IGNORECASE
            )

            if match:
                term_1 = match.group(1)
                term_2 = match.group(2)

                return (
                    f"{term_1} का उपयोग "
                    f"{term_2} करता है"
                )

        # ----------------------------------------------------
        # Unknown text
        # ----------------------------------------------------

        # A real translation provider will replace this
        # behavior.
        return text


# ============================================================
# 3. ENGLISH → HINDI TRANSLATOR
# ============================================================

class EnglishHindiTranslator:
    """
    Main English → Hindi translation pipeline.

    Pipeline:

        English input
             ↓
        Detect glossary terms
             ↓
        Protect important terms
             ↓
        Translate
             ↓
        Restore preferred terminology
             ↓
        Validate
    """

    def __init__(
        self,
        glossary_engine: Any,
        provider: TranslationProvider
    ):
        self.glossary = glossary_engine
        self.provider = provider

    # --------------------------------------------------------
    # Create translator from glossary file
    # --------------------------------------------------------

    @classmethod
    def from_glossary_file(
        cls,
        glossary_path: str,
        provider: TranslationProvider
    ):
        """
        Create a translator using a glossary JSON file.
        """

        glossary = load_glossary(glossary_path)

        return cls(
            glossary_engine=glossary,
            provider=provider
        )

    # --------------------------------------------------------
    # STEP 1: Detect glossary terms
    # --------------------------------------------------------

    def detect_terms(
        self,
        text: str
    ) -> List[Dict[str, Any]]:
        """
        Detect glossary terms.

        Supports:
        1. A glossary engine object with find_terms()
        2. The real Day 3 glossary list
        """

        # If an object provides its own find_terms()
        # method, use it.
        if hasattr(self.glossary, "find_terms"):
            return self.glossary.find_terms(text)

        # Otherwise use the real Day 3 function.
        return find_terms(
            text,
            self.glossary
        )

    # --------------------------------------------------------
    # STEP 2: Protect glossary terms
    # --------------------------------------------------------

    def protect_terms(
        self,
        text: str,
        terms: List[Dict[str, Any]]
    ):
        """
        Replace glossary terms with safe placeholders.

        Example:

        Patent protection is important.

        becomes:

        __TERM_0__ protection is important.
        """

        protected_text = text
        protected_terms: Dict[str, Dict[str, Any]] = {}

        # Longer terms are processed first.
        sorted_terms = sorted(
            terms,
            key=lambda item: len(
                item.get("matched_text", "")
            ),
            reverse=True
        )

        for index, term in enumerate(sorted_terms):

            matched_text = term.get("matched_text")

            if not matched_text:
                continue

            placeholder = f"__TERM_{index}__"

            pattern = re.compile(
                re.escape(matched_text),
                re.IGNORECASE
            )

            if pattern.search(protected_text):

                protected_text = pattern.sub(
                    placeholder,
                    protected_text,
                    count=1
                )

                protected_terms[placeholder] = term

        return protected_text, protected_terms

    # --------------------------------------------------------
    # STEP 3: Translate
    # --------------------------------------------------------

    def translate_text(
        self,
        text: str
    ) -> str:
        """
        Send protected text to the selected translation provider.
        """

        return self.provider.translate(
            text,
            source="en",
            target="hi"
        )

    # --------------------------------------------------------
    # STEP 4: Restore preferred terminology
    # --------------------------------------------------------

    def restore_terms(
        self,
        translated_text: str,
        protected_terms: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Replace glossary placeholders with preferred Hindi terminology.

        Supports the different glossary field names used by
        the Day 3 glossary and the Day 4 mock glossary.
        """

        result = translated_text

        for placeholder, term in protected_terms.items():
            # Support all glossary formats
            preferred_hi = (
                term.get("preferred_hindi")
                or term.get("preferred_hi")
                or term.get("hindi")
            )

            if not preferred_hi:
                continue

            # Replace placeholder case-insensitively.
            pattern = re.compile(
                re.escape(placeholder),
                re.IGNORECASE
            )

            result = pattern.sub(
                preferred_hi,
                result
            )

        return result

    # --------------------------------------------------------
    # STEP 5: Validate
    # --------------------------------------------------------

    def validate(
        self,
        original_text: str,
        translated_text: str,
        terms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate the translated result.

        Checks whether the preferred Hindi terminology appears
        in the final output.
        """

        missing_terms = []

        for term in terms:
            preferred_hi = term.get("preferred_hindi")

            if preferred_hi and preferred_hi not in translated_text:
                missing_terms.append({
                    "term_id": term.get("term_id"),
                    "matched_text": term.get("matched_text"),
                    "expected_hi": preferred_hi
                })

        return {
            "valid": len(missing_terms) == 0,
            "missing_terms": missing_terms,
            "original_text": original_text,
            "translated_text": translated_text
        }

    # --------------------------------------------------------
    # COMPLETE TRANSLATION PIPELINE
    # --------------------------------------------------------

    def translate(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Run the complete English → Hindi pipeline.
        """

        # ----------------------------------------------------
        # Input validation
        # ----------------------------------------------------

        if not isinstance(text, str):
            raise TypeError(
                "Input text must be a string."
            )

        if not text.strip():
            raise ValueError(
                "Input text cannot be empty."
            )

        # ----------------------------------------------------
        # 1. Detect glossary terms
        # ----------------------------------------------------

        terms = self.detect_terms(text)

        # ----------------------------------------------------
        # 2. Protect glossary terms
        # ----------------------------------------------------

        protected_text, protected_terms = (
            self.protect_terms(
                text,
                terms
            )
        )

        # ----------------------------------------------------
        # 3. Translate protected text
        # ----------------------------------------------------

        translated_text = self.translate_text(
            protected_text
        )

        # ----------------------------------------------------
        # 4. Restore preferred terminology
        # ----------------------------------------------------

        final_text = self.restore_terms(
            translated_text,
            protected_terms
        )

        # ----------------------------------------------------
        # 5. Validate
        # ----------------------------------------------------

        validation = self.validate(
            text,
            final_text,
            terms
        )

        # ----------------------------------------------------
        # Return complete pipeline result
        # ----------------------------------------------------

        return {
            "source": "en",
            "target": "hi",
            "original": text,
            "detected_terms": terms,
            "protected_text": protected_text,
            "translated_text": translated_text,
            "final_translation": final_text,
            "validation": validation
        }