"""
services/ai_ocr_service.py
==========================
Service OCR pour transcrire les copies manuscrites avec OpenAI Vision
"""

import base64
import io
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

from openai import OpenAI
import fitz  # PyMuPDF

from ..config import settings


class OCRProcessor:
    """Processeur OCR utilisant GPT-4 Vision pour les copies manuscrites"""

    def __init__(self):
        self.client = self._init_openai_client()
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.webp', '.gif']

    def _init_openai_client(self) -> OpenAI:
        """Initialise le client OpenAI"""
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("Cle API OpenAI manquante")
        return OpenAI(api_key=api_key)

    def transcribe_file(
        self,
        file_path: str,
        matiere: str = "general",
        detailed: bool = True
    ) -> Dict:
        """
        Transcrit un fichier (PDF ou image) en texte

        Args:
            file_path: Chemin vers le fichier
            matiere: Matiere pour adapter la transcription
            detailed: Si True, retourne une analyse detaillee

        Returns:
            Dict avec transcription et metadonnees
        """
        path = Path(file_path)

        if not path.exists():
            return self._error_result(f"Fichier non trouve: {file_path}")

        if path.suffix.lower() not in self.supported_formats:
            return self._error_result(f"Format non supporte: {path.suffix}")

        try:
            if path.suffix.lower() == '.pdf':
                return self._transcribe_pdf(path, matiere, detailed)
            else:
                return self._transcribe_image(path, matiere, detailed)
        except Exception as e:
            return self._error_result(str(e))

    def transcribe_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        matiere: str = "general",
        detailed: bool = True
    ) -> Dict:
        """
        Transcrit des bytes (upload direct) en texte

        Args:
            file_bytes: Contenu du fichier en bytes
            filename: Nom du fichier pour determiner le format
            matiere: Matiere pour adapter la transcription
            detailed: Si True, retourne une analyse detaillee

        Returns:
            Dict avec transcription et metadonnees
        """
        suffix = Path(filename).suffix.lower()

        if suffix not in self.supported_formats:
            return self._error_result(f"Format non supporte: {suffix}")

        try:
            if suffix == '.pdf':
                return self._transcribe_pdf_bytes(file_bytes, matiere, detailed)
            else:
                return self._transcribe_image_bytes(file_bytes, matiere, detailed)
        except Exception as e:
            return self._error_result(str(e))

    def _transcribe_pdf(self, path: Path, matiere: str, detailed: bool) -> Dict:
        """Transcrit un PDF page par page"""
        doc = fitz.open(str(path))
        all_text = []
        page_results = []

        for page_num, page in enumerate(doc):
            # Convertir la page en image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_bytes = pix.tobytes("png")

            # Transcrire l'image
            page_result = self._transcribe_image_bytes(img_bytes, matiere, detailed)
            page_results.append({
                "page": page_num + 1,
                "text": page_result.get("transcribed_text", ""),
                "confidence": page_result.get("confidence", 0)
            })
            all_text.append(page_result.get("transcribed_text", ""))

        doc.close()

        full_text = "\n\n--- Page suivante ---\n\n".join(all_text)

        return {
            "transcribed_text": full_text,
            "confidence": sum(p["confidence"] for p in page_results) / len(page_results) if page_results else 0,
            "page_count": len(page_results),
            "pages": page_results,
            "matiere": matiere,
            "processing_time": datetime.now().isoformat(),
            "word_count": len(full_text.split()),
            "character_count": len(full_text)
        }

    def _transcribe_pdf_bytes(self, pdf_bytes: bytes, matiere: str, detailed: bool) -> Dict:
        """Transcrit un PDF depuis des bytes"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        all_text = []
        page_results = []

        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")

            page_result = self._transcribe_image_bytes(img_bytes, matiere, detailed)
            page_results.append({
                "page": page_num + 1,
                "text": page_result.get("transcribed_text", ""),
                "confidence": page_result.get("confidence", 0)
            })
            all_text.append(page_result.get("transcribed_text", ""))

        doc.close()

        full_text = "\n\n--- Page suivante ---\n\n".join(all_text)

        return {
            "transcribed_text": full_text,
            "confidence": sum(p["confidence"] for p in page_results) / len(page_results) if page_results else 0,
            "page_count": len(page_results),
            "pages": page_results,
            "matiere": matiere,
            "processing_time": datetime.now().isoformat(),
            "word_count": len(full_text.split()),
            "character_count": len(full_text)
        }

    def _transcribe_image(self, path: Path, matiere: str, detailed: bool) -> Dict:
        """Transcrit une image"""
        with open(path, "rb") as f:
            img_bytes = f.read()
        return self._transcribe_image_bytes(img_bytes, matiere, detailed)

    def _transcribe_image_bytes(self, img_bytes: bytes, matiere: str, detailed: bool) -> Dict:
        """Transcrit une image depuis des bytes avec GPT-4 Vision"""

        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        prompt = self._build_ocr_prompt(matiere, detailed)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1
            )

            transcription = response.choices[0].message.content

            # Analyser la qualite de la transcription
            confidence = self._estimate_confidence(transcription)

            return {
                "transcribed_text": transcription,
                "confidence": confidence,
                "matiere": matiere,
                "processing_time": datetime.now().isoformat(),
                "word_count": len(transcription.split()),
                "character_count": len(transcription),
                "model_used": "gpt-4o"
            }

        except Exception as e:
            return self._error_result(str(e))

    def _build_ocr_prompt(self, matiere: str, detailed: bool) -> str:
        """Construit le prompt OCR adapte a la matiere"""

        base_prompt = """Tu es un expert en transcription de copies manuscrites d'examens.
Transcris fidelement le texte ecrit a la main dans cette image.

INSTRUCTIONS IMPORTANTES :
1. Transcris TOUT le texte visible, meme s'il est difficile a lire
2. Conserve la structure (paragraphes, listes, numerotation)
3. Si un mot est illisible, indique [illisible]
4. Si tu n'es pas sur d'un mot, indique [mot?]
5. Preserve les formules mathematiques en LaTeX si applicable
6. Ne corrige PAS les fautes d'orthographe de l'etudiant
7. Indique les ratures avec [rature: texte barre]
"""

        matiere_instructions = {
            "mathematiques": """
INSTRUCTIONS SPECIFIQUES MATHEMATIQUES :
- Transcris les formules en notation LaTeX
- Preserve les etapes de calcul
- Indique les schemas/graphiques avec [Schema: description]
- Attention aux exposants, indices et symboles speciaux
""",
            "physique": """
INSTRUCTIONS SPECIFIQUES PHYSIQUE :
- Transcris les formules en LaTeX
- Preserve les unites (m, kg, s, etc.)
- Indique les schemas avec [Schema: description]
- Attention aux vecteurs et symboles physiques
""",
            "francais": """
INSTRUCTIONS SPECIFIQUES FRANCAIS :
- Preserve la ponctuation exacte
- Conserve les guillemets et citations
- Indique les paragraphes clairement
- Ne corrige PAS les fautes
""",
            "general": """
- Transcris fidelement sans interpretation
- Preserve la mise en page originale
"""
        }

        prompt = base_prompt + matiere_instructions.get(matiere.lower(), matiere_instructions["general"])

        if detailed:
            prompt += """

A la fin de ta transcription, ajoute une section:
---
ANALYSE:
- Qualite d'ecriture: [BONNE/MOYENNE/DIFFICILE]
- Mots incertains: [liste]
- Observations: [notes sur la copie]
"""

        prompt += "\n\nTranscris maintenant cette copie :"

        return prompt

    def _estimate_confidence(self, transcription: str) -> float:
        """Estime la confiance de la transcription"""

        uncertain_markers = ['[illisible]', '[mot?]', '?]', '[rature']
        uncertain_count = sum(transcription.lower().count(marker) for marker in uncertain_markers)

        word_count = len(transcription.split())
        if word_count == 0:
            return 0.0

        uncertainty_ratio = uncertain_count / word_count
        confidence = max(0.5, 1.0 - (uncertainty_ratio * 5))

        return round(min(1.0, confidence), 2)

    def _error_result(self, error_message: str) -> Dict:
        """Retourne un resultat d'erreur"""
        return {
            "transcribed_text": f"[ERREUR: {error_message}]",
            "confidence": 0.0,
            "error": error_message,
            "processing_time": datetime.now().isoformat(),
            "word_count": 0,
            "character_count": 0
        }


# Interface simple
def transcribe_manuscript(
    file_path: str,
    matiere: str = "general"
) -> Dict:
    """Interface simple pour transcrire un fichier"""
    processor = OCRProcessor()
    return processor.transcribe_file(file_path, matiere)


def transcribe_manuscript_bytes(
    file_bytes: bytes,
    filename: str,
    matiere: str = "general"
) -> Dict:
    """Interface simple pour transcrire des bytes"""
    processor = OCRProcessor()
    return processor.transcribe_bytes(file_bytes, filename, matiere)