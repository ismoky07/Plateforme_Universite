"""
services/ai_correction_service.py
=================================
Moteur de correction IA integre avec commentaires intelligents par question
Compatible avec la structure FastAPI
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import OpenAI

from ..config import settings


class SpecializedPromptBuilder:
    """Constructeur de prompts specialises par matiere"""

    def __init__(self):
        self.subject_specializations = {
            "Mathematiques": self._get_math_specialization,
            "Mathematique": self._get_math_specialization,
            "Maths": self._get_math_specialization,
            "Physique": self._get_physics_specialization,
            "Physique-Chimie": self._get_physics_specialization,
            "Chimie": self._get_chemistry_specialization,
            "Francais": self._get_french_specialization,
            "Lettres": self._get_french_specialization,
            "Histoire": self._get_history_specialization,
            "Geographie": self._get_geography_specialization,
            "Philosophie": self._get_philosophy_specialization,
            "Anglais": self._get_english_specialization,
            "Biologie": self._get_biology_specialization,
            "SVT": self._get_biology_specialization,
            "Economie": self._get_economics_specialization,
            "Informatique": self._get_default_specialization,
        }

    def get_specialized_expertise(self, matiere: str) -> Dict[str, str]:
        """Retourne l'expertise specialisee pour une matiere"""
        specialization_func = self.subject_specializations.get(
            matiere, self._get_default_specialization
        )
        return specialization_func()

    def _get_math_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree de MATHEMATIQUES avec 15 ans d'experience",
            "expertise_specifique": """
**EXPERTISE MATHEMATIQUE AVANCEE :**
- Maitrise parfaite des concepts algebriques, analytiques et geometriques
- Specialiste de l'analyse des erreurs de raisonnement mathematique
- Expert en pedagogie differenciee selon les profils d'apprentissage""",
            "criteres_specialises": """
**EVALUATION TECHNIQUE MATHEMATIQUE :**
- Exactitude des calculs (40%)
- Rigueur methodologique (35%)
- Logique deductive (20%)
- Presentation formelle (5%)""",
            "diagnostic_avance": """
**ANALYSE DIFFERENTIELLE PAR TYPE D'ERREUR :**
- Confusion notations
- Domaines de definition
- Calculs trigonometriques
- Analyse dimensionnelle""",
            "ressources_pedagogiques": """
**RESSOURCES MATHEMATIQUES CIBLEES :**
- Pour l'algebre : Exercices sur les systemes lineaires
- Pour l'analyse : Problemes de continuite, derivabilite"""
        }

    def _get_physics_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree de PHYSIQUE",
            "expertise_specifique": """
**EXPERTISE PHYSIQUE SPECIALISEE :**
- Maitrise de la mecanique, electromagnetisme, thermodynamique
- Specialiste de l'analyse dimensionnelle""",
            "criteres_specialises": """
**EVALUATION TECHNIQUE PHYSIQUE :**
- Analyse dimensionnelle (30%)
- Application des lois (35%)
- Calculs et approximations (25%)
- Interpretation physique (10%)""",
            "diagnostic_avance": "Analyse par domaine physique",
            "ressources_pedagogiques": "Simulations PhET, Python/Matplotlib"
        }

    def _get_chemistry_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree de CHIMIE",
            "expertise_specifique": "Expertise en chimie organique et analytique",
            "criteres_specialises": "Equilibrage, mecanismes, nomenclature, securite",
            "diagnostic_avance": "Analyse acide-base, oxydo-reduction, cinetique",
            "ressources_pedagogiques": "ChemSketch, spectroscopie"
        }

    def _get_french_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree de LETTRES MODERNES",
            "expertise_specifique": "Analyse litteraire et commentaire compose",
            "criteres_specialises": "Argumentation (40%), Culture (30%), Langue (20%), Style (10%)",
            "diagnostic_avance": "Dissertation, commentaire, ecriture creative",
            "ressources_pedagogiques": "Corpus litteraire, methodes"
        }

    def _get_history_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree d'HISTOIRE",
            "expertise_specifique": "Histoire contemporaine et analyse documentaire",
            "criteres_specialises": "Connaissances (35%), Analyse (30%), Argumentation (25%)",
            "diagnostic_avance": "Chronologie, sources primaires, historiographie",
            "ressources_pedagogiques": "Archives, cartographie historique"
        }

    def _get_geography_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree de GEOGRAPHIE",
            "expertise_specifique": "Geographie humaine et physique",
            "criteres_specialises": "Localisation (25%), Analyse (35%), Croquis (25%)",
            "diagnostic_avance": "Cartographie, territoires, environnement",
            "ressources_pedagogiques": "SIG, donnees statistiques"
        }

    def _get_philosophy_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree de PHILOSOPHIE",
            "expertise_specifique": "Philosophie morale et politique",
            "criteres_specialises": "Problematisation (35%), Argumentation (30%), References (25%)",
            "diagnostic_avance": "Conceptualisation, dialectique, hermeneutique",
            "ressources_pedagogiques": "Textes fondamentaux, dictionnaires"
        }

    def _get_english_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur certifie d'ANGLAIS",
            "expertise_specifique": "Litterature et civilisation anglophone",
            "criteres_specialises": "Correction (40%), Expression (30%), Culture (20%)",
            "diagnostic_avance": "Grammar, Vocabulary, Cultural Knowledge",
            "ressources_pedagogiques": "Cambridge, Oxford, BBC"
        }

    def _get_biology_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree de BIOLOGIE",
            "expertise_specifique": "Biologie cellulaire et ecologie",
            "criteres_specialises": "Connaissances (40%), Raisonnement (30%), Schemas (20%)",
            "diagnostic_avance": "Cellulaire, genetique, ecologie, physiologie",
            "ressources_pedagogiques": "Microscopie, experimentation"
        }

    def _get_economics_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agree d'ECONOMIE",
            "expertise_specifique": "Microeconomie et macroeconomie",
            "criteres_specialises": "Theories (35%), Graphiques (30%), Calculs (25%)",
            "diagnostic_avance": "Micro, macro, international, public",
            "ressources_pedagogiques": "INSEE, OCDE, graphiques"
        }

    def _get_default_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "correcteur expert multidisciplinaire",
            "expertise_specifique": "Methodes d'evaluation transversales",
            "criteres_specialises": "Pertinence (40%), Exactitude (35%), Methode (15%), Expression (10%)",
            "diagnostic_avance": "Analyse, synthese, argumentation, communication",
            "ressources_pedagogiques": "Methodologie, expression, analyse critique"
        }


class AICorrectionEngine:
    """Moteur de correction IA integre"""

    def __init__(self):
        """Initialise le moteur IA"""
        self.client = self._init_openai_client()
        self.prompt_builder = SpecializedPromptBuilder()
        self.correction_profiles = {
            "excellence": {
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 3000,
            },
            "equilibre": {
                "model": "gpt-4o",
                "temperature": 0.2,
                "max_tokens": 2500,
            },
            "rapide": {
                "model": "gpt-4o-mini",
                "temperature": 0.3,
                "max_tokens": 2000,
            }
        }

    def _init_openai_client(self) -> OpenAI:
        """Initialise le client OpenAI"""
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("Cle API OpenAI manquante. Configurez OPENAI_API_KEY")
        return OpenAI(api_key=api_key)

    def process_evaluation_copies(
        self,
        evaluation_info: Dict,
        copies_data: List[Dict],
        profile: str = "equilibre"
    ) -> List[Dict]:
        """
        Traite toutes les copies d'une evaluation avec l'IA specialisee

        Args:
            evaluation_info: Informations de l'evaluation
            copies_data: Liste des copies avec leurs transcriptions
            profile: Profil de correction ("excellence", "equilibre", "rapide")

        Returns:
            Liste des resultats de correction
        """
        if profile not in self.correction_profiles:
            profile = "equilibre"

        config = self.correction_profiles[profile]
        results = []

        matiere = evaluation_info.get('matiere', 'General')
        specialized_expertise = self.prompt_builder.get_specialized_expertise(matiere)
        bareme = evaluation_info.get('bareme', self._get_default_bareme())

        for i, copy_data in enumerate(copies_data):
            try:
                # Correction par expert IA
                correction = self._correct_with_ai_expert(
                    copy_data.get('transcription', ''),
                    bareme,
                    evaluation_info,
                    config,
                    specialized_expertise
                )

                # Formatage du resultat
                result = self._format_result(
                    correction,
                    copy_data.get('etudiant_nom', f'Etudiant{i+1}'),
                    copy_data.get('etudiant_prenom', f'Prenom{i+1}'),
                    i + 1,
                    profile,
                    bareme,
                    specialized_expertise
                )

                results.append(result)

            except Exception as e:
                error_result = self._create_error_result(
                    copy_data.get('etudiant_nom', f'Etudiant{i+1}'),
                    copy_data.get('etudiant_prenom', f'Prenom{i+1}'),
                    str(e),
                    i + 1
                )
                results.append(error_result)

        return results

    def correct_single_copy(
        self,
        transcription: str,
        evaluation_info: Dict,
        student_name: str,
        student_firstname: str,
        profile: str = "equilibre"
    ) -> Dict:
        """Corrige une seule copie"""

        if profile not in self.correction_profiles:
            profile = "equilibre"

        config = self.correction_profiles[profile]
        matiere = evaluation_info.get('matiere', 'General')
        specialized_expertise = self.prompt_builder.get_specialized_expertise(matiere)
        bareme = evaluation_info.get('bareme', self._get_default_bareme())

        try:
            correction = self._correct_with_ai_expert(
                transcription,
                bareme,
                evaluation_info,
                config,
                specialized_expertise
            )

            return self._format_result(
                correction,
                student_name,
                student_firstname,
                1,
                profile,
                bareme,
                specialized_expertise
            )
        except Exception as e:
            return self._create_error_result(student_name, student_firstname, str(e), 1)

    def _correct_with_ai_expert(
        self,
        transcription: str,
        bareme: Dict,
        evaluation_info: Dict,
        config: Dict,
        specialized_expertise: Dict
    ) -> Dict:
        """Correction par expert IA (GPT-4)"""

        prompt = self._build_expert_prompt(bareme, evaluation_info, specialized_expertise)

        try:
            response = self.client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Voici la copie a corriger :\n\n{transcription}"}
                ],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )

            correction_text = response.choices[0].message.content
            return self._parse_expert_response(correction_text)

        except Exception as e:
            return {
                "note_totale": 0.0,
                "commentaires": f"Erreur correction IA: {str(e)}",
                "details": {}
            }

    def _build_expert_prompt(
        self,
        bareme: Dict,
        evaluation_info: Dict,
        specialized_expertise: Dict
    ) -> str:
        """Construit le prompt pour l'expert correcteur"""

        matiere = evaluation_info.get('matiere', 'General')
        classe = evaluation_info.get('classe', 'Inconnue')
        note_totale = bareme.get('note_totale', 20)

        prompt = f"""Tu es un {specialized_expertise['titre_expert']} pour la classe {classe}.

{specialized_expertise['expertise_specifique']}

**MISSION : CORRECTION EXPERTE**
Corrige cette copie d'examen selon les criteres academiques.

**BAREME DE L'EVALUATION :**
- Matiere: {matiere}
- Note totale: {note_totale} points

{specialized_expertise['criteres_specialises']}

**QUESTIONS ET CRITERES :**"""

        for question in bareme.get('questions', []):
            prompt += f"""
Question {question.get('numero', 1)}: {question.get('intitule', 'Question')}
- Points: {question.get('points_total', 5)}
- Type: {question.get('type', 'ouverte')}
"""

        prompt += f"""

**FORMAT DE REPONSE OBLIGATOIRE :**
```
NOTE_FINALE: X.X/{note_totale}

DETAIL_PAR_QUESTION:"""

        for i, question in enumerate(bareme.get('questions', []), 1):
            prompt += f"""
Q{i}: X.X/{question.get('points_total', 5)} - [POURCENTAGE: XX%]
COMMENTAIRE_Q{i}: [Commentaire personnalise]
CONSEIL_Q{i}: [Conseil specifique]"""

        prompt += """

POINTS_FORTS:
- [Point fort 1]
- [Point fort 2]

POINTS_AMELIORATION:
- [Point amelioration 1]
- [Point amelioration 2]

COMMENTAIRE_GENERAL:
[Commentaire global]

CONSEILS_PERSONNALISES:
- [Conseil 1]
- [Conseil 2]

DIAGNOSTIC_PERFORMANCE:
[Diagnostic global]
```

Analyse maintenant cette copie :"""

        return prompt

    def _parse_expert_response(self, response_text: str) -> Dict:
        """Parse la reponse de l'expert IA"""

        result = {
            "note_totale": 0.0,
            "notes_par_question": {},
            "commentaires_par_question": {},
            "conseils_par_question": {},
            "pourcentages_par_question": {},
            "points_forts": [],
            "points_amelioration": [],
            "commentaires": "",
            "conseils": [],
            "diagnostic_performance": ""
        }

        try:
            lines = response_text.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()

                if line.startswith('NOTE_FINALE:'):
                    note_str = line.split(':')[1].strip()
                    if '/' in note_str:
                        try:
                            result["note_totale"] = float(note_str.split('/')[0])
                        except ValueError:
                            pass

                elif line.startswith('Q') and ':' in line and '/' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        q_num = parts[0].strip()
                        note_part = parts[1].split('-')[0].strip()
                        if '/' in note_part:
                            try:
                                result["notes_par_question"][q_num] = float(note_part.split('/')[0])
                            except ValueError:
                                pass

                        if 'POURCENTAGE:' in line:
                            try:
                                pct = line.split('POURCENTAGE:')[1].split('%')[0].strip()
                                result["pourcentages_par_question"][q_num] = float(pct)
                            except (ValueError, IndexError):
                                pass

                elif line.startswith('COMMENTAIRE_Q') and ':' in line:
                    try:
                        q_num = line.split('_Q')[1].split(':')[0].strip()
                        comment = ':'.join(line.split(':')[1:]).strip()
                        result["commentaires_par_question"][f"Q{q_num}"] = comment
                    except (IndexError, ValueError):
                        pass

                elif line.startswith('CONSEIL_Q') and ':' in line:
                    try:
                        q_num = line.split('_Q')[1].split(':')[0].strip()
                        conseil = ':'.join(line.split(':')[1:]).strip()
                        result["conseils_par_question"][f"Q{q_num}"] = conseil
                    except (IndexError, ValueError):
                        pass

                elif line.startswith('DIAGNOSTIC_PERFORMANCE:'):
                    result["diagnostic_performance"] = ':'.join(line.split(':')[1:]).strip()

                elif line == 'POINTS_FORTS:':
                    current_section = 'points_forts'
                elif line == 'POINTS_AMELIORATION:':
                    current_section = 'points_amelioration'
                elif line == 'COMMENTAIRE_GENERAL:':
                    current_section = 'commentaires'
                elif line == 'CONSEILS_PERSONNALISES:':
                    current_section = 'conseils'

                elif current_section and line and not line.startswith('```'):
                    if line.startswith('- '):
                        content = line[2:].strip()
                        if current_section == 'points_forts':
                            result["points_forts"].append(content)
                        elif current_section == 'points_amelioration':
                            result["points_amelioration"].append(content)
                        elif current_section == 'conseils':
                            result["conseils"].append(content)
                    elif current_section == 'commentaires' and len(line) > 5:
                        result["commentaires"] = line

        except Exception as e:
            result["commentaires"] = f"Erreur parsing: {str(e)}"

        return result

    def _format_result(
        self,
        correction: Dict,
        student_name: str,
        student_firstname: str,
        rank: int,
        profile: str,
        bareme: Dict,
        specialized_expertise: Dict
    ) -> Dict:
        """Formate le resultat"""

        note_totale = correction.get("note_totale", 0.0)
        note_max = bareme.get('note_totale', 20.0)

        questions_detaillees = []
        for i, question_bareme in enumerate(bareme.get('questions', []), 1):
            q_key = f"Q{i}"
            note_question = correction.get("notes_par_question", {}).get(q_key, 0.0)
            note_max_q = question_bareme.get('points_total', 5.0)

            pourcentage = correction.get("pourcentages_par_question", {}).get(q_key)
            if pourcentage is None and note_max_q > 0:
                pourcentage = round((note_question / note_max_q) * 100, 1)

            questions_detaillees.append({
                "numero": question_bareme.get('numero', i),
                "intitule": question_bareme.get('intitule', f'Question {i}'),
                "type": question_bareme.get('type', 'ouverte'),
                "note": note_question,
                "note_max": note_max_q,
                "commentaire_intelligent": correction.get("commentaires_par_question", {}).get(q_key, ""),
                "conseil_personnalise": correction.get("conseils_par_question", {}).get(q_key, ""),
                "pourcentage_reussite": pourcentage or 0.0
            })

        return {
            "etudiant_nom": student_name,
            "etudiant_prenom": student_firstname,
            "note_totale": round(note_totale, 1),
            "note_maximale": note_max,
            "pourcentage": round((note_totale / note_max) * 100, 1) if note_max > 0 else 0.0,
            "rang_classe": rank,
            "timestamp": datetime.now().isoformat(),
            "commentaires_generaux": correction.get("commentaires", ""),
            "points_forts": correction.get("points_forts", [])[:3],
            "points_amelioration": correction.get("points_amelioration", [])[:3],
            "conseils_personnalises": correction.get("conseils", [])[:3],
            "diagnostic_performance": correction.get("diagnostic_performance", ""),
            "questions": questions_detaillees,
            "qualite_correction": {
                "profil_utilise": profile.title(),
                "modele_ia": self.correction_profiles[profile]["model"],
                "expertise_specialisee": specialized_expertise['titre_expert']
            }
        }

    def _get_default_bareme(self) -> Dict:
        """Bareme par defaut"""
        return {
            "note_totale": 20,
            "questions": [
                {
                    "numero": 1,
                    "intitule": "Question generale",
                    "points_total": 20,
                    "type": "ouverte"
                }
            ]
        }

    def _create_error_result(
        self,
        student_name: str,
        student_firstname: str,
        error_msg: str,
        rank: int
    ) -> Dict:
        """Cree un resultat d'erreur"""
        return {
            "etudiant_nom": student_name,
            "etudiant_prenom": student_firstname,
            "note_totale": 0.0,
            "note_maximale": 20.0,
            "pourcentage": 0.0,
            "rang_classe": rank,
            "timestamp": datetime.now().isoformat(),
            "commentaires_generaux": f"Erreur lors de la correction: {error_msg}",
            "points_forts": [],
            "points_amelioration": ["Correction manuelle necessaire"],
            "conseils_personnalises": ["Contactez l'enseignant"],
            "diagnostic_performance": "Erreur de traitement",
            "questions": [],
            "necessite_revision_humaine": True,
            "qualite_correction": {
                "profil_utilise": "Erreur",
                "modele_ia": "error"
            }
        }


# Interface simple
def process_copies_with_ai(
    evaluation_info: Dict,
    copies_data: List[Dict],
    profile: str = "equilibre"
) -> List[Dict]:
    """Interface simple pour traiter les copies avec l'IA"""
    engine = AICorrectionEngine()
    return engine.process_evaluation_copies(evaluation_info, copies_data, profile)


def correct_single_copy_with_ai(
    transcription: str,
    evaluation_info: Dict,
    student_name: str,
    student_firstname: str,
    profile: str = "equilibre"
) -> Dict:
    """Corrige une seule copie"""
    engine = AICorrectionEngine()
    return engine.correct_single_copy(
        transcription, evaluation_info, student_name, student_firstname, profile
    )
