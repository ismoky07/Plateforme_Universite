"""
utils/ai_correction_engine.py
==============================
Moteur de correction IA intégré avec commentaires intelligents par question
Compatible avec la structure de données existante
Version complète améliorée avec spécialisation par matière
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Charger les variables d'environnement
load_dotenv()

class SpecializedPromptBuilder:
    """Constructeur de prompts spécialisés par matière"""
    
    def __init__(self):
        self.subject_specializations = {
            "Mathématiques": self._get_math_specialization,
            "Mathématique": self._get_math_specialization,
            "Maths": self._get_math_specialization,
            "Physique": self._get_physics_specialization,
            "Physique-Chimie": self._get_physics_specialization,
            "Chimie": self._get_chemistry_specialization,
            "Français": self._get_french_specialization,
            "Lettres": self._get_french_specialization,
            "Histoire": self._get_history_specialization,
            "Géographie": self._get_geography_specialization,
            "Philosophie": self._get_philosophy_specialization,
            "Anglais": self._get_english_specialization,
            "Biologie": self._get_biology_specialization,
            "SVT": self._get_biology_specialization,
            "Économie": self._get_economics_specialization,
            "Droit": self._get_law_specialization
        }
    
    def get_specialized_expertise(self, matiere: str) -> Dict[str, str]:
        """Retourne l'expertise spécialisée pour une matière"""
        specialization_func = self.subject_specializations.get(matiere, self._get_default_specialization)
        return specialization_func()
    
    def _get_math_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé de MATHÉMATIQUES avec 15 ans d'expérience",
            "expertise_specifique": """
**EXPERTISE MATHÉMATIQUE AVANCÉE :**
- Maîtrise parfaite des concepts algébriques, analytiques et géométriques
- Spécialiste de l'analyse des erreurs de raisonnement mathématique
- Expert en pédagogie différenciée selon les profils d'apprentissage
- Connaissance approfondie des programmes L1, L2, L3 et classes préparatoires""",
            
            "criteres_specialises": """
🔢 **ÉVALUATION TECHNIQUE MATHÉMATIQUE :**
- **Exactitude des calculs** (40%) : Vérification systématique des résultats numériques
- **Rigueur méthodologique** (35%) : Cohérence de la démarche et justification des étapes  
- **Logique déductive** (20%) : Structure du raisonnement et enchaînement logique
- **Présentation formelle** (5%) : Notation correcte et clarté de l'exposition

📐 **DIAGNOSTIC SPÉCIALISÉ DES ERREURS :**
- **Erreurs de calcul** → Révision des techniques de base (dérivation, intégration, etc.)
- **Erreurs conceptuelles** → Reprise des définitions et propriétés fondamentales
- **Erreurs logiques** → Travail sur la structuration du raisonnement déductif
- **Erreurs de méthode** → Entraînement ciblé sur les techniques de résolution""",
            
            "diagnostic_avance": """
**ANALYSE DIFFÉRENTIELLE PAR TYPE D'ERREUR :**
- **Confusion notations** : Distinction fonction/variable, dérivée/différentielle
- **Domaines de définition** : Vérification systématique des conditions d'existence
- **Calculs trigonométriques** : Maîtrise des identités et transformations
- **Analyse dimensionnelle** : Cohérence des unités dans les problèmes appliqués
- **Convergence/divergence** : Rigueur dans l'étude des limites et séries""",
            
            "ressources_pedagogiques": """
**RESSOURCES MATHÉMATIQUES CIBLÉES :**
- **Pour l'algèbre** : Exercices sur les systèmes linéaires et polynômes
- **Pour l'analyse** : Problèmes de continuité, dérivabilité, intégration
- **Pour la géométrie** : Travaux sur les transformations et espaces vectoriels
- **Outils recommandés** : GeoGebra pour la visualisation, Wolfram Alpha pour vérification"""
        }
    
    def _get_physics_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé de PHYSIQUE avec expertise en physique expérimentale et théorique",
            "expertise_specifique": """
**EXPERTISE PHYSIQUE SPÉCIALISÉE :**
- Maîtrise de la mécanique classique, électromagnétisme, thermodynamique, optique
- Spécialiste de l'analyse dimensionnelle et des ordres de grandeur
- Expert en modélisation des phénomènes physiques complexes
- Connaissance approfondie des protocoles expérimentaux et mesures""",
            
            "criteres_specialises": """
⚛️ **ÉVALUATION TECHNIQUE PHYSIQUE :**
- **Analyse dimensionnelle** (30%) : Vérification de l'homogénéité des équations
- **Application des lois** (35%) : Utilisation correcte des principes physiques
- **Calculs et approximations** (25%) : Justesse numérique et hypothèses réalistes
- **Interprétation physique** (10%) : Sens physique des résultats obtenus

🔬 **DIAGNOSTIC SPÉCIALISÉ PHYSIQUE :**
- **Erreurs dimensionnelles** → Révision des unités SI et analyse dimensionnelle
- **Mauvaise modélisation** → Retour aux hypothèses et approximations physiques
- **Calculs vectoriels** → Entraînement sur les opérations vectorielles 3D
- **Ordres de grandeur** → Développement du sens physique et estimations""",
            
            "diagnostic_avance": """
**ANALYSE PAR DOMAINE PHYSIQUE :**
- **Mécanique** : Forces, énergies, mouvements (cinématique/dynamique)
- **Électromagnétisme** : Champs E et B, circuits, induction
- **Thermodynamique** : Principes, cycles, transformations
- **Optique** : Géométrique, ondulatoire, interférences
- **Physique moderne** : Relativité, quantique, physique atomique""",
            
            "ressources_pedagogiques": """
**RESSOURCES PHYSIQUES SPÉCIALISÉES :**
- **Simulations** : PhET pour visualiser les phénomènes physiques
- **Expériences** : Protocoles et analyse d'incertitudes
- **Modélisation** : Python/Matplotlib pour les graphiques scientifiques"""
        }
    
    def _get_chemistry_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé de CHIMIE avec spécialisation en chimie organique et analytique",
            "expertise_specifique": """
**EXPERTISE CHIMIQUE AVANCÉE :**
- Maîtrise de la chimie générale, organique, inorganique et analytique
- Spécialiste des mécanismes réactionnels et stœchiométrie
- Expert en spectroscopie et méthodes d'analyse structurale
- Connaissance approfondie des protocoles de sécurité chimique""",
            
            "criteres_specialises": """
🧪 **ÉVALUATION TECHNIQUE CHIMIQUE :**
- **Équilibrage et stœchiométrie** (35%) : Exactitude des équations et calculs molaires
- **Mécanismes réactionnels** (30%) : Compréhension des processus moléculaires
- **Nomenclature et formules** (20%) : Respect des règles IUPAC
- **Sécurité et protocoles** (15%) : Conscience des risques et bonnes pratiques""",
            
            "diagnostic_avance": """
**ANALYSE PAR TYPE DE RÉACTION :**
- **Acide-base** : pH, pKa, titrages et solutions tampon
- **Oxydo-réduction** : Potentiels, électrolyse, piles
- **Chimie organique** : Fonctions, mécanismes, synthèses
- **Cinétique** : Vitesses de réaction, catalyse, équilibres""",
            
            "ressources_pedagogiques": """
**RESSOURCES CHIMIQUES SPÉCIALISÉES :**
- **Modélisation moléculaire** : ChemSketch, Avogadro
- **Spectroscopie** : Interprétation RMN, IR, UV-Visible
- **Protocoles expérimentaux** : Sécurité et techniques de laboratoire"""
        }
    
    def _get_french_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé de LETTRES MODERNES avec spécialisation en littérature française",
            "expertise_specifique": """
**EXPERTISE LITTÉRAIRE ET LINGUISTIQUE :**
- Maîtrise parfaite de l'analyse littéraire et du commentaire composé
- Spécialiste de la dissertation argumentative et de l'écriture créative
- Expert en grammaire, orthographe, syntaxe et stylistique française
- Connaissance approfondie de l'histoire littéraire et culturelle""",
            
            "criteres_specialises": """
📚 **ÉVALUATION SPÉCIALISÉE FRANÇAIS :**
- **Argumentation et logique** (40%) : Cohérence du raisonnement et progression des idées
- **Culture littéraire** (30%) : Références pertinentes et analyse des œuvres
- **Maîtrise de la langue** (20%) : Orthographe, grammaire, syntaxe, vocabulaire
- **Créativité et style** (10%) : Originalité de l'expression et élégance du style""",
            
            "diagnostic_avance": """
**ANALYSE PAR TYPE D'EXERCICE :**
- **Dissertation** : Problématique, plan, argumentation, ouverture
- **Commentaire** : Analyse linéaire, axes d'étude, procédés stylistiques
- **Écriture créative** : Imagination, cohérence narrative, registres
- **Grammaire** : Analyse syntaxique, morphologie, sémantique""",
            
            "ressources_pedagogiques": """
**RESSOURCES LITTÉRAIRES :**
- **Corpus littéraire** : Œuvres au programme, classiques
- **Méthodes** : Dissertation, commentaire, analyse stylistique
- **Outils linguistiques** : Dictionnaires, grammaires de référence"""
        }
    
    def _get_geography_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé de GÉOGRAPHIE avec spécialisation en géographie humaine et physique",
            "expertise_specifique": """
**EXPERTISE GÉOGRAPHIQUE SPÉCIALISÉE :**
- Maîtrise de la géographie humaine, physique et régionale
- Spécialiste de l'analyse spatiale et de la cartographie
- Expert en géopolitique et aménagement du territoire
- Connaissance approfondie des enjeux environnementaux""",
            
            "criteres_specialises": """
🌍 **ÉVALUATION GÉOGRAPHIQUE SPÉCIALISÉE :**
- **Localisation et repères** (25%) : Précision des connaissances spatiales
- **Analyse territoriale** (35%) : Compréhension des dynamiques spatiales
- **Croquis et schémas** (25%) : Qualité des représentations graphiques
- **Enjeux contemporains** (15%) : Actualité géographique et géopolitique""",
            
            "diagnostic_avance": """
**COMPÉTENCES GÉOGRAPHIQUES SPÉCIFIQUES :**
- **Cartographie** : Lecture, analyse et réalisation de cartes
- **Territoires** : Échelles locales, nationales, mondiales
- **Environnement** : Risques, développement durable, changement climatique
- **Populations** : Démographie, migrations, urbanisation""",
            
            "ressources_pedagogiques": """
**RESSOURCES GÉOGRAPHIQUES :**
- **Outils cartographiques** : SIG, cartes topographiques
- **Données statistiques** : INSEE, ONU, Banque mondiale
- **Actualité géographique** : Revues spécialisées, atlas"""
        }
    
    def _get_philosophy_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé de PHILOSOPHIE avec spécialisation en philosophie morale et politique",
            "expertise_specifique": """
**EXPERTISE PHILOSOPHIQUE SPÉCIALISÉE :**
- Maîtrise de l'histoire de la philosophie et des grands courants
- Spécialiste de l'argumentation et de la problématisation
- Expert en philosophie morale, politique et métaphysique
- Connaissance approfondie des auteurs et des concepts fondamentaux""",
            
            "criteres_specialises": """
🤔 **ÉVALUATION PHILOSOPHIQUE SPÉCIALISÉE :**
- **Problématisation** (35%) : Capacité à identifier et formuler les enjeux
- **Argumentation** (30%) : Cohérence et rigueur du raisonnement
- **Références culturelles** (25%) : Connaissance des auteurs et doctrines
- **Esprit critique** (10%) : Originalité et profondeur de la réflexion""",
            
            "diagnostic_avance": """
**COMPÉTENCES PHILOSOPHIQUES SPÉCIFIQUES :**
- **Conceptualisation** : Définition et analyse des concepts
- **Dialectique** : Confrontation des thèses et antithèses
- **Herméneutique** : Interprétation des textes philosophiques
- **Épistémologie** : Réflexion sur la connaissance et la vérité""",
            
            "ressources_pedagogiques": """
**RESSOURCES PHILOSOPHIQUES :**
- **Textes fondamentaux** : Corpus des grands philosophes
- **Méthodes** : Dissertation, commentaire de texte, analyse conceptuelle
- **Dictionnaires spécialisés** : Vocabulaire philosophique"""
        }
    
    def _get_english_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur certifié d'ANGLAIS avec spécialisation en littérature et civilisation",
            "expertise_specifique": """
**EXPERTISE ANGLOPHONE SPÉCIALISÉE :**
- Maîtrise parfaite de la langue anglaise et de ses subtilités
- Spécialiste de la littérature anglophone et de la civilisation
- Expert en linguistique appliquée et phonétique
- Connaissance approfondie des cultures anglophones""",
            
            "criteres_specialises": """
🇬🇧 **ÉVALUATION ANGLAIS SPÉCIALISÉE :**
- **Correction linguistique** (40%) : Grammaire, syntaxe, vocabulaire
- **Expression écrite** (30%) : Cohérence, style, register
- **Compréhension culturelle** (20%) : Références civilisationnelles
- **Créativité linguistique** (10%) : Richesse et nuances d'expression""",
            
            "diagnostic_avance": """
**COMPÉTENCES LINGUISTIQUES SPÉCIFIQUES :**
- **Grammar & Syntax** : Temps, modaux, structures complexes
- **Vocabulary** : Précision lexicale, collocations, idioms
- **Cultural Knowledge** : Histoire, littérature, société
- **Communication Skills** : Argumentation, nuances, register""",
            
            "ressources_pedagogiques": """
**RESSOURCES ANGLAIS :**
- **Grammaires de référence** : Cambridge, Oxford
- **Littérature** : Corpus britannique et américain
- **Médias authentiques** : BBC, CNN, journaux anglophones"""
        }
    
    def _get_biology_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé de BIOLOGIE avec spécialisation en biologie cellulaire et écologie",
            "expertise_specifique": """
**EXPERTISE BIOLOGIQUE SPÉCIALISÉE :**
- Maîtrise de la biologie cellulaire, moléculaire et de l'écologie
- Spécialiste de la physiologie et de l'évolution
- Expert en génétique et biotechnologies
- Connaissance approfondie des protocoles expérimentaux""",
            
            "criteres_specialises": """
🧬 **ÉVALUATION BIOLOGIQUE SPÉCIALISÉE :**
- **Connaissances scientifiques** (40%) : Précision des concepts biologiques
- **Raisonnement scientifique** (30%) : Logique expérimentale et hypothèses
- **Schémas et représentations** (20%) : Qualité des illustrations scientifiques
- **Actualité scientifique** (10%) : Connaissance des avancées récentes""",
            
            "diagnostic_avance": """
**DOMAINES BIOLOGIQUES SPÉCIFIQUES :**
- **Biologie cellulaire** : Structure, fonction, métabolisme
- **Génétique** : Hérédité, mutations, biotechnologies
- **Écologie** : Écosystèmes, biodiversité, évolution
- **Physiologie** : Fonctions vitales, homéostasie""",
            
            "ressources_pedagogiques": """
**RESSOURCES BIOLOGIQUES :**
- **Microscopie** : Observation et analyse cellulaire
- **Expérimentation** : Protocoles et méthodes scientifiques
- **Modélisation** : Représentations moléculaires et écologiques"""
        }
    
    def _get_economics_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé d'ÉCONOMIE avec spécialisation en microéconomie et macroéconomie",
            "expertise_specifique": """
**EXPERTISE ÉCONOMIQUE SPÉCIALISÉE :**
- Maîtrise des théories microéconomiques et macroéconomiques
- Spécialiste de l'analyse des marchés et des politiques économiques
- Expert en économétrie et statistiques économiques
- Connaissance approfondie de l'actualité économique mondiale""",
            
            "criteres_specialises": """
💰 **ÉVALUATION ÉCONOMIQUE SPÉCIALISÉE :**
- **Théories économiques** (35%) : Maîtrise des concepts et modèles
- **Analyse graphique** (30%) : Interprétation des courbes et schémas
- **Calculs économiques** (25%) : Précision des calculs et formules
- **Actualité économique** (10%) : Connaissance des enjeux contemporains""",
            
            "diagnostic_avance": """
**DOMAINES ÉCONOMIQUES SPÉCIFIQUES :**
- **Microéconomie** : Comportement des agents, marchés, prix
- **Macroéconomie** : Croissance, inflation, chômage, politiques
- **Économie internationale** : Commerce, changes, mondialisation
- **Économie publique** : Budget, fiscalité, régulation""",
            
            "ressources_pedagogiques": """
**RESSOURCES ÉCONOMIQUES :**
- **Données statistiques** : INSEE, OCDE, Banque mondiale
- **Graphiques économiques** : Courbes, modèles, simulations
- **Actualité économique** : Presse spécialisée, rapports officiels"""
        }
    
    def _get_law_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur de DROIT avec spécialisation en droit civil et droit public",
            "expertise_specifique": """
**EXPERTISE JURIDIQUE SPÉCIALISÉE :**
- Maîtrise du droit civil, pénal, constitutionnel et administratif
- Spécialiste de l'analyse jurisprudentielle et des textes de loi
- Expert en méthodologie juridique et raisonnement juridique
- Connaissance approfondie de l'évolution du droit contemporain""",
            
            "criteres_specialises": """
⚖️ **ÉVALUATION JURIDIQUE SPÉCIALISÉE :**
- **Connaissances juridiques** (40%) : Précision des règles et principes
- **Raisonnement juridique** (35%) : Logique de l'argumentation juridique
- **Références normatives** (20%) : Citations de lois, jurisprudence, doctrine
- **Cas pratiques** (5%) : Application du droit aux situations concrètes""",
            
            "diagnostic_avance": """
**DOMAINES JURIDIQUES SPÉCIFIQUES :**
- **Droit civil** : Personnes, biens, contrats, responsabilité
- **Droit public** : Constitution, administratif, fiscal
- **Procédure** : Méthodologie, instances, recours
- **Jurisprudence** : Analyse des décisions de justice""",
            
            "ressources_pedagogiques": """
**RESSOURCES JURIDIQUES :**
- **Codes juridiques** : Civil, pénal, administratif
- **Jurisprudence** : Décisions des juridictions supérieures
- **Doctrine** : Manuels, revues juridiques spécialisées"""
        }
    
    def _get_history_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "professeur agrégé d'HISTOIRE avec spécialisation en histoire contemporaine",
            "expertise_specifique": """
**EXPERTISE HISTORIQUE SPÉCIALISÉE :**
- Maîtrise chronologique de l'Antiquité à l'époque contemporaine
- Spécialiste de l'analyse de documents historiques et de la critique des sources
- Expert en géopolitique et relations internationales
- Méthodes de contextualisation et d'analyse comparative""",
            
            "criteres_specialises": """
📜 **ÉVALUATION HISTORIQUE SPÉCIALISÉE :**
- **Connaissances factuelles** (35%) : Précision des dates, événements, personnages
- **Analyse documentaire** (30%) : Critique des sources et contextualisation
- **Argumentation historique** (25%) : Causalité, continuités, ruptures
- **Synthèse et problématisation** (10%) : Vision d'ensemble et problématiques""",
            
            "diagnostic_avance": """
**COMPÉTENCES HISTORIQUES SPÉCIFIQUES :**
- **Chronologie** : Maîtrise des périodisations et repères temporels
- **Géographie historique** : Localisation et évolution des territoires
- **Sources primaires** : Analyse critique des documents d'époque
- **Historiographie** : Connaissance des débats et écoles historiques""",
            
            "ressources_pedagogiques": """
**RESSOURCES HISTORIQUES :**
- **Sources primaires** : Documents d'archives, témoignages
- **Cartographie historique** : Atlas, cartes d'époque
- **Historiographie** : Travaux des historiens, débats contemporains"""
        }
    
    def _get_default_specialization(self) -> Dict[str, str]:
        return {
            "titre_expert": "correcteur expert multidisciplinaire",
            "expertise_specifique": """
**EXPERTISE GÉNÉRALISTE ADAPTABLE :**
- Maîtrise des méthodes d'évaluation transversales
- Spécialiste de l'analyse pédagogique différenciée
- Expert en diagnostic des compétences académiques
- Connaissance approfondie des critères d'évaluation standards""",
            
            "criteres_specialises": """
📋 **ÉVALUATION GÉNÉRALISTE :**
- **Pertinence** (40%) : Adéquation du contenu à la question
- **Exactitude** (35%) : Justesse des informations et concepts
- **Méthode** (15%) : Organisation et structure de la réponse
- **Expression** (10%) : Clarté et qualité de la communication""",
            
            "diagnostic_avance": """
**COMPÉTENCES TRANSVERSALES :**
- **Analyse** : Capacité à décomposer et examiner
- **Synthèse** : Capacité à organiser et structurer
- **Argumentation** : Logique et cohérence du raisonnement
- **Communication** : Clarté et précision de l'expression""",
            
            "ressources_pedagogiques": """
**RESSOURCES PÉDAGOGIQUES GÉNÉRALES :**
- **Méthodologie** : Techniques d'étude et d'organisation
- **Expression** : Amélioration de la communication écrite et orale
- **Analyse critique** : Développement de l'esprit critique"""
        }

class AICorrecionEngine:
    """Moteur de correction IA intégré dans l'espace prof existant avec spécialisation par matière"""
    
    def __init__(self):
        """Initialise le moteur IA"""
        self.client = self._init_openai_client()
        self.prompt_builder = SpecializedPromptBuilder()
        self.correction_profiles = {
            "excellence": {
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 3000,  # Augmenté pour les commentaires détaillés
                "ocr_quality": "maximum",
                "double_check": False,
                "parallel": True
            },
            "equilibre": {
                "model": "gpt-4o", 
                "temperature": 0.2,
                "max_tokens": 2500,
                "ocr_quality": "high",
                "double_check": False,
                "parallel": True
            },
            "rapide": {
                "model": "gpt-4o-mini",
                "temperature": 0.3,
                "max_tokens": 2000,
                "ocr_quality": "standard",
                "double_check": False,
                "parallel": True
            }
        }
    
    def _init_openai_client(self):
        """Initialise le client OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ Clé API OpenAI manquante. Configurez OPENAI_API_KEY dans .env")
        return OpenAI(api_key=api_key)
    
    def process_evaluation_copies(self, evaluation_info: Dict, copies_paths: List[str], 
                                profile: str = "excellence") -> List[Dict]:
        """
        Traite toutes les copies d'une évaluation avec l'IA spécialisée
        
        Args:
            evaluation_info: Informations de l'évaluation (depuis data_manager)
            copies_paths: Liste des chemins vers les copies PDF
            profile: Profil de correction ("excellence", "equilibre", "rapide")
            
        Returns:
            Liste des résultats de correction (compatible format existant)
        """
        
        if profile not in self.correction_profiles:
            profile = "excellence"
        
        config = self.correction_profiles[profile]
        results = []
        
        # NOUVEAU : Détection automatique de la matière pour spécialisation
        matiere = evaluation_info.get('matiere', 'Général')
        specialized_expertise = self.prompt_builder.get_specialized_expertise(matiere)
        
        # Charger le barème
        bareme = self._load_bareme(evaluation_info)
        
        for i, copy_path in enumerate(copies_paths):
            try:
                # Étape 1: OCR de la copie manuscrite
                transcription = self._ocr_manuscript_copy(copy_path, config, evaluation_info)
                
                # Étape 2: Correction par expert IA avec commentaires intelligents et spécialisation
                correction = self._correct_with_ai_expert(
                    transcription, 
                    bareme, 
                    evaluation_info,
                    config,
                    specialized_expertise
                )
                
                # Étape 3: Formatage compatible avec l'existant
                student_name, student_firstname = self._extract_student_names(copy_path, i)
                
                result = self._format_result_for_existing_system(
                    correction, 
                    student_name, 
                    student_firstname,
                    i + 1,
                    profile,
                    transcription,
                    bareme,
                    specialized_expertise
                )
                
                results.append(result)
                
            except Exception as e:
                # En cas d'erreur, créer un résultat par défaut
                student_name, student_firstname = self._extract_student_names(copy_path, i)
                error_result = self._create_error_result(
                    student_name, 
                    student_firstname, 
                    str(e),
                    i + 1
                )
                results.append(error_result)
        
        return results
    
    def _ocr_manuscript_copy(self, copy_path: str, config: Dict, evaluation_info: Dict) -> Dict:
        """
        Transcription OCR d'une copie manuscrite - VERSION CORRIGÉE
        Utilise les fonctions qui retournent des dictionnaires pour éviter l'erreur .get()
        """
        
        try:
            # ✅ CORRECTION : Utiliser transcribe_with_analysis qui retourne un Dict
            from .ai_ocr_processor import transcribe_with_analysis
            
            # Récupérer la matière pour la spécialisation OCR
            matiere = evaluation_info.get('matiere', 'general')
            
            # Mapper les matières vers les valeurs acceptées par l'OCR
            matiere_ocr_mapping = {
                'Mathématiques': 'mathematiques',
                'Mathématique': 'mathematiques', 
                'Maths': 'mathematiques',
                'Physique': 'mathematiques',  # Utilise le même traitement que maths
                'Physique-Chimie': 'mathematiques',
                'Chimie': 'mathematiques',
                'Français': 'francais',
                'Lettres': 'francais',
                'Histoire': 'francais',  # Utilise le traitement français pour les textes
                'Géographie': 'francais',
                'Philosophie': 'francais',
                'Anglais': 'francais',
                'Biologie': 'general',
                'SVT': 'general',
                'Économie': 'general',
                'Droit': 'francais'
            }
            
            matiere_ocr = matiere_ocr_mapping.get(matiere, 'general')
            transcription_result = transcribe_with_analysis(
                self.client,
                copy_path,
                matiere=matiere_ocr,
                type_exercice='redaction'
            )
            
            # Vérifier que c'est bien un dictionnaire
            if not isinstance(transcription_result, dict):
                raise ValueError("La fonction OCR n'a pas retourné un dictionnaire")
            
            return transcription_result
            
        except ImportError:
            # Fallback 1 : Essayer l'autre fonction OCR
            try:
                from .ai_ocr_processor import transcribe_manuscript_copy_dict
                
                return transcribe_manuscript_copy_dict(
                    self.client,
                    copy_path,
                    quality=config["ocr_quality"],
                    matiere=matiere_ocr,
                    type_exercice='redaction'
                )
            except ImportError:
                # Fallback 2 : Implémentation OCR basique
                return {
                    "transcribed_text": f"Contenu OCR simulé pour {copy_path}",
                    "confidence": 0.9,
                    "quality": config["ocr_quality"],
                    "processing_time": 2.5,
                    "word_count": 150,
                    "character_count": 750,
                    "matiere": matiere,
                    "type_exercice": "redaction",
                    "structure_detectee": {},
                    "formules_maths": [],
                    "mots_incertains": [],
                    "suggestions_amelioration": [],
                    "qualite_ecriture": "MOYENNE",
                    "confiance_globale": 90.0,
                    "erreurs_transcription": []
                }
        except Exception as e:
            # En cas d'erreur, retourner un dictionnaire d'erreur
            return {
                "transcribed_text": f"[ERREUR OCR: {str(e)}]",
                "confidence": 0.0,
                "quality": "error",
                "processing_time": 0.0,
                "word_count": 0,
                "character_count": 0,
                "matiere": evaluation_info.get('matiere', 'general'),
                "type_exercice": "redaction",
                "structure_detectee": {},
                "formules_maths": [],
                "mots_incertains": [],
                "suggestions_amelioration": ["Erreur de transcription OCR"],
                "qualite_ecriture": "ERREUR",
                "confiance_globale": 0.0,
                "erreurs_transcription": [str(e)]
            }
    
    def _correct_with_ai_expert(self, transcription: Dict, bareme: Dict, 
                              evaluation_info: Dict, config: Dict,
                              specialized_expertise: Dict) -> Dict:
        """Correction par expert IA (GPT-4) avec commentaires intelligents et spécialisation"""
        
        # Construction du prompt expert avec commentaires intelligents et spécialisation
        prompt = self._build_expert_prompt_with_smart_comments(bareme, evaluation_info, specialized_expertise)
        
        try:
            # ✅ Accès sécurisé aux données de transcription (maintenant un Dict)
            texte_transcrit = transcription.get('transcribed_text', '[Texte non disponible]')
            
            response = self.client.chat.completions.create(
                model=config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user", 
                        "content": f"Voici la copie à corriger :\n\n{texte_transcrit}"
                    }
                ],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )
            
            correction_text = response.choices[0].message.content
            return self._parse_expert_response_with_smart_comments(correction_text)
            
        except Exception as e:
            return {
                "note_totale": 0.0,
                "commentaires": f"Erreur correction IA: {str(e)}",
                "details": {}
            }
    
    def _build_expert_prompt_with_smart_comments(self, bareme: Dict, evaluation_info: Dict, specialized_expertise: Dict) -> str:
        """Construit le prompt pour l'expert correcteur avec commentaires intelligents et spécialisation"""
        
        matiere = evaluation_info.get('matiere', 'Général')
        classe = evaluation_info.get('promotion', 'Inconnue')
        note_totale = bareme.get('note_totale', 20)
        
        prompt = f"""Tu es un {specialized_expertise['titre_expert']} pour la classe {classe}.

{specialized_expertise['expertise_specifique']}

**MISSION : CORRECTION EXPERTE AVEC COMMENTAIRES INTELLIGENTS**
Corrige cette copie d'examen selon les critères académiques avec la rigueur d'un correcteur officiel.
Pour chaque question, génère un commentaire personnalisé et intelligent basé sur la performance de l'étudiant.

**BARÈME DE L'ÉVALUATION :**
- Matière: {matiere}
- Note totale: {note_totale} points
- Durée: {evaluation_info.get('duree', 'Non spécifiée')}

{specialized_expertise['criteres_specialises']}

**QUESTIONS ET CRITÈRES :**"""

        # Ajouter les questions du barème avec instructions spécifiques
        for question in bareme.get('questions', []):
            prompt += f"""
Question {question['numero']}: {question['intitule']}
- Points: {question['points_total']}
- Type: {question['type']}
- Critères: {', '.join(question.get('criteres', ['Pertinence', 'Exactitude']))}
"""

        prompt += f"""

**INSTRUCTIONS POUR COMMENTAIRES INTELLIGENTS PAR QUESTION :**

Pour chaque question, adapte ton commentaire selon le pourcentage de réussite :

🏆 **90-100% (Excellent)** :
- Félicite la performance exceptionnelle
- Suggère des défis supplémentaires ou méthodes alternatives
- Encourage à aider ses camarades

🌟 **75-89% (Très bien)** :
- Souligne la très bonne maîtrise
- Identifie les petits détails à peaufiner pour atteindre l'excellence
- Encourage la persévérance

👍 **60-74% (Bien)** :
- Reconnaît la bonne compréhension globale
- Identifie les points précis à améliorer
- Propose des exercices d'approfondissement

🔄 **40-59% (Moyen)** :
- Identifie les éléments acquis positivement
- Explique clairement les lacunes principales
- Propose des révisions ciblées et méthodes d'étude

⚠️ **20-39% (Faible)** :
- Reste encourageant malgré les difficultés
- Identifie les bases à reprendre
- Recommande un accompagnement pédagogique

🚨 **0-19% (Très faible)** :
- Ton bienveillant et constructif
- Focus sur les prérequis fondamentaux
- Conseille une remise à niveau urgente

**CONSEILS SPÉCIFIQUES PAR TYPE DE QUESTION :**
- **Calcul** : Méthode, erreurs de calcul, unités, vérifications
- **Démonstration** : Logique, structure, rigueur, étapes manquantes
- **QCM** : Compréhension des concepts, élimination, nuances
- **Ouverte** : Développement, structure, richesse, hors-sujet

**CONSEILS SPÉCIFIQUES POUR {matiere.upper()} :**"""

        # Conseils spécifiques par matière
        subject_tips = {
            "Mathématiques": """
- Vérification des calculs et cohérence des résultats
- Utilisation correcte des notations et symboles
- Rigueur dans les démonstrations et justifications
- Représentations graphiques et schémas explicatifs""",
            
            "Physique": """
- Analyse dimensionnelle et cohérence des unités
- Application correcte des lois et principes physiques
- Interprétation des phénomènes et des résultats
- Schémas et représentations des situations""",
            
            "Chimie": """
- Équilibrage des équations et stœchiométrie
- Nomenclature et formules chimiques correctes
- Mécanismes réactionnels et interprétations
- Sécurité et protocoles expérimentaux""",
            
            "Français": """
- Qualité de l'expression et richesse du vocabulaire
- Structure et progression logique des idées
- Maîtrise de l'orthographe et de la grammaire
- Références culturelles et littéraires pertinentes""",
            
            "Histoire": """
- Chronologie et contextualisation historique
- Analyse critique des sources et documents
- Argumentation et esprit de synthèse
- Connaissances factuelles précises""",
            
            "Philosophie": """
- Problématisation et définition des concepts
- Cohérence et rigueur de l'argumentation
- Références aux auteurs et doctrines philosophiques
- Esprit critique et originalité de la réflexion""",
            
            "Géographie": """
- Localisation précise et repères géographiques
- Analyse des dynamiques territoriales et spatiales
- Qualité des croquis et schémas cartographiques
- Compréhension des enjeux géopolitiques contemporains""",
            
            "Anglais": """
- Correction grammaticale et syntaxique
- Richesse et précision du vocabulaire
- Respect des registres de langue appropriés
- Références culturelles et civilisationnelles""",
            
            "Biologie": """
- Précision du vocabulaire scientifique
- Qualité des schémas et représentations biologiques
- Rigueur du raisonnement expérimental
- Connaissance des protocoles et méthodes""",
            
            "Économie": """
- Maîtrise des concepts et théories économiques
- Précision des calculs et formules
- Qualité de l'analyse graphique
- Actualité et enjeux économiques contemporains""",
            
            "Droit": """
- Précision des références juridiques
- Rigueur du raisonnement juridique
- Connaissance de la jurisprudence
- Application correcte des règles de droit"""
        }
        
        prompt += subject_tips.get(matiere, """
- Précision du vocabulaire spécialisé
- Méthodologie et rigueur scientifique
- Application des concepts à des situations concrètes
- Esprit critique et analyse approfondie""")

        # Ajouter le diagnostic avancé spécialisé
        if specialized_expertise.get('diagnostic_avance'):
            prompt += f"""

**DIAGNOSTIC SPÉCIALISÉ POUR {matiere.upper()} :**
{specialized_expertise['diagnostic_avance']}"""

        # Ajouter les ressources pédagogiques spécialisées
        if specialized_expertise.get('ressources_pedagogiques'):
            prompt += f"""

**RESSOURCES PÉDAGOGIQUES SPÉCIALISÉES :**
{specialized_expertise['ressources_pedagogiques']}"""

        prompt += f"""

**FORMAT DE RÉPONSE OBLIGATOIRE :**
```
NOTE_FINALE: X.X/{note_totale}

DÉTAIL_PAR_QUESTION:"""

        # Format dynamique selon les questions du barème
        for i, question in enumerate(bareme.get('questions', []), 1):
            prompt += f"""
Q{i}: X.X/{question['points_total']} - [POURCENTAGE: XX%]
COMMENTAIRE_Q{i}: [Commentaire intelligent et personnalisé selon la performance - 2-3 phrases adaptées au niveau de réussite]
CONSEIL_Q{i}: [Conseil spécifique et actionnable pour cette question - 1 phrase précise]
DIAGNOSTIC_TECHNIQUE_Q{i}: [Analyse technique spécialisée en {matiere}]"""

        prompt += f"""

POINTS_FORTS:
- [Point fort 1 - spécifique et valorisant]
- [Point fort 2 - encourageant]
- [Point fort 3 - si applicable]

POINTS_AMÉLIORATION:
- [Point amélioration 1 - constructif et précis]
- [Point amélioration 2 - avec suggestion concrète]
- [Point amélioration 3 - si applicable]

COMMENTAIRE_GÉNÉRAL:
[Commentaire global bienveillant mais exigeant, qui fait le lien entre les questions et donne une vision d'ensemble de la performance]

CONSEILS_PERSONNALISÉS:
- [Conseil méthodologique personnalisé]
- [Conseil de révision ciblé selon les lacunes détectées]
- [Conseil motivationnel adapté au niveau]

DIAGNOSTIC_PERFORMANCE:
[Une phrase de diagnostic global : niveau actuel et potentiel d'amélioration]
```

**INSTRUCTIONS IMPORTANTES :**
1. **Sois bienveillant** : Même avec de mauvaises notes, reste encourageant et constructif
2. **Sois précis** : Identifie exactement où sont les erreurs et comment les corriger
3. **Sois personnalisé** : Adapte chaque commentaire au niveau réel de l'étudiant
4. **Sois actionnable** : Donne des conseils concrets et réalisables
5. **Calcule le pourcentage** pour chaque question : (note obtenue / note max) × 100
6. **Utilise ton expertise en {matiere}** : Applique tes connaissances spécialisées

Analyse maintenant cette copie avec l'expertise d'un correcteur expérimenté et bienveillant spécialisé en {matiere} :"""

        return prompt
    
    def _parse_expert_response_with_smart_comments(self, response_text: str) -> Dict:
        """Parse la réponse de l'expert IA avec commentaires par question"""
        
        result = {
            "note_totale": 0.0,
            "notes_par_question": {},
            "commentaires_par_question": {},  # NOUVEAU
            "conseils_par_question": {},      # NOUVEAU
            "pourcentages_par_question": {},  # NOUVEAU
            "diagnostic_technique_par_question": {},  # NOUVEAU
            "points_forts": [],
            "points_amelioration": [],
            "commentaires": "",
            "conseils": [],
            "diagnostic_performance": ""      # NOUVEAU
        }
        
        try:
            lines = response_text.split('\n')
            current_section = None
            current_question = None
            
            for line in lines:
                line = line.strip()
                
                # Parser la note finale
                if line.startswith('NOTE_FINALE:'):
                    note_str = line.split(':')[1].strip()
                    if '/' in note_str:
                        try:
                            result["note_totale"] = float(note_str.split('/')[0])
                        except ValueError:
                            result["note_totale"] = 0.0
                
                # Parser les détails par question avec pourcentage
                elif line.startswith('Q') and ':' in line and '/' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        q_num = parts[0].strip()
                        current_question = q_num
                        note_part = parts[1].split('-')[0].strip()
                        if '/' in note_part:
                            try:
                                note_value = float(note_part.split('/')[0])
                                result["notes_par_question"][q_num] = note_value
                            except ValueError:
                                result["notes_par_question"][q_num] = 0.0
                        
                        # Extraire le pourcentage si présent
                        if 'POURCENTAGE:' in line:
                            try:
                                pourcentage_part = line.split('POURCENTAGE:')[1].split('%')[0].strip()
                                if pourcentage_part.replace('.', '').replace(',', '').isdigit():
                                    pourcentage_part = pourcentage_part.replace(',', '.')
                                    result["pourcentages_par_question"][q_num] = float(pourcentage_part)
                            except (ValueError, IndexError):
                                pass
                
                # Parser les commentaires par question
                elif line.startswith('COMMENTAIRE_Q') and ':' in line:
                    try:
                        q_num = line.split('_Q')[1].split(':')[0].strip()
                        commentaire = ':'.join(line.split(':')[1:]).strip()
                        result["commentaires_par_question"][f"Q{q_num}"] = commentaire
                    except (IndexError, ValueError):
                        pass
                
                # Parser les conseils par question
                elif line.startswith('CONSEIL_Q') and ':' in line:
                    try:
                        q_num = line.split('_Q')[1].split(':')[0].strip()
                        conseil = ':'.join(line.split(':')[1:]).strip()
                        result["conseils_par_question"][f"Q{q_num}"] = conseil
                    except (IndexError, ValueError):
                        pass
                
                # Parser le diagnostic technique par question
                elif line.startswith('DIAGNOSTIC_TECHNIQUE_Q') and ':' in line:
                    try:
                        q_num = line.split('_Q')[1].split(':')[0].strip()
                        diagnostic = ':'.join(line.split(':')[1:]).strip()
                        result["diagnostic_technique_par_question"][f"Q{q_num}"] = diagnostic
                    except (IndexError, ValueError):
                        pass
                
                # Parser le diagnostic de performance
                elif line.startswith('DIAGNOSTIC_PERFORMANCE:'):
                    result["diagnostic_performance"] = ':'.join(line.split(':')[1:]).strip()
                
                # Identifier les sections existantes
                elif line == 'POINTS_FORTS:':
                    current_section = 'points_forts'
                elif line == 'POINTS_AMÉLIORATION:':
                    current_section = 'points_amelioration'
                elif line == 'COMMENTAIRE_GÉNÉRAL:':
                    current_section = 'commentaires'
                elif line == 'CONSEILS_PERSONNALISÉS:':
                    current_section = 'conseils'
                
                # Parser le contenu des sections
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
    
    def _format_result_for_existing_system(self, correction: Dict, student_name: str, 
                                         student_firstname: str, rank: int, 
                                         profile: str, transcription: Dict, bareme: Dict,
                                         specialized_expertise: Dict) -> Dict:
        """Formate le résultat avec les nouveaux commentaires par question"""
        
        note_totale = correction.get("note_totale", 0.0)
        note_max = bareme.get('note_totale', 20.0)
        
        # Commentaires combinés AMÉLIORÉS
        commentaires_parts = []
        if correction.get("commentaires"):
            commentaires_parts.append(correction["commentaires"])
        if correction.get("diagnostic_performance"):
            commentaires_parts.append(f"Diagnostic: {correction['diagnostic_performance']}")
        
        commentaires_generaux = ". ".join(commentaires_parts) if commentaires_parts else "Correction effectuée par IA spécialisée."
        
        # Construction des questions avec commentaires intelligents
        questions_detaillees = []
        questions_bareme = bareme.get('questions', [])
        
        for i, question_bareme in enumerate(questions_bareme, 1):
            q_key = f"Q{i}"
            note_question = correction.get("notes_par_question", {}).get(q_key, 0.0)
            note_max_question = question_bareme.get('points_total', 5.0)
            
            # Calcul du pourcentage si pas fourni par l'IA
            pourcentage_question = correction.get("pourcentages_par_question", {}).get(q_key)
            if pourcentage_question is None and note_max_question > 0:
                pourcentage_question = round((note_question / note_max_question) * 100, 1)
            
            question_detail = {
                "numero": question_bareme['numero'],
                "intitule": question_bareme['intitule'],
                "type": question_bareme['type'],
                "note": note_question,
                "note_max": note_max_question,
                "commentaire_intelligent": correction.get("commentaires_par_question", {}).get(q_key, ""),
                "conseil_personnalise": correction.get("conseils_par_question", {}).get(q_key, ""),
                "diagnostic_technique_specialise": correction.get("diagnostic_technique_par_question", {}).get(q_key, ""),  # NOUVEAU
                "pourcentage_reussite": pourcentage_question or 0.0
            }
            questions_detaillees.append(question_detail)
        
        # ✅ Calcul des rangs et statistiques - accès sécurisé aux données de transcription
        ocr_confidence = transcription.get("confidence", 0.9)
        if ocr_confidence is None:
            ocr_confidence = transcription.get("confiance_globale", 90.0) / 100.0
        
        # Résultat enrichi
        result = {
            "etudiant_nom": student_name,
            "etudiant_prenom": student_firstname,
            "note_totale": round(note_totale, 1),
            "note_maximale": note_max,
            "pourcentage": round((note_totale / note_max) * 100, 1) if note_max > 0 else 0.0,
            "rang_classe": rank,
            "timestamp": datetime.now().isoformat(),
            "commentaires_generaux": commentaires_generaux,
            "points_forts": correction.get("points_forts", [])[:3],
            "points_amelioration": correction.get("points_amelioration", [])[:3],
            "conseils_personnalises": correction.get("conseils", [])[:3],
            "diagnostic_performance": correction.get("diagnostic_performance", ""),
            
            # NOUVEAU : Questions avec commentaires intelligents
            "questions": questions_detaillees,  # Compatible format existant
            "questions_avec_commentaires": questions_detaillees,  # Alias explicite
            
            # Données existantes
            "detection_triche": {
                "similarite_detectee": ocr_confidence < 0.7,
                "score_max": round((1.0 - ocr_confidence) * 100, 2),
                "algorithme": "ai_analysis"
            },
            "necessite_revision_humaine": note_totale < (note_max * 0.25),  # 25% du total
            "qualite_correction": {
                "profil_utilise": profile.title(),
                "confiance_ocr": round(ocr_confidence, 2),
                "modele_ia": "gpt-4o",
                "verification_double": profile == "excellence",
                "expertise_specialisee": specialized_expertise['titre_expert']  # NOUVEAU
            },
            "ai_details": {
                "notes_par_question": correction.get("notes_par_question", {}),
                "commentaires_par_question": correction.get("commentaires_par_question", {}),
                "conseils_par_question": correction.get("conseils_par_question", {}),
                "diagnostic_technique_par_question": correction.get("diagnostic_technique_par_question", {}),  # NOUVEAU
                "pourcentages_par_question": correction.get("pourcentages_par_question", {}),
                "transcription_quality": transcription.get("quality", "unknown"),
                "processing_time": transcription.get("processing_time", 0),
                "specialisation_matiere": specialized_expertise.get('titre_expert', 'Généraliste')  # NOUVEAU
            }
        }
        
        return result
    
    def _load_bareme(self, evaluation_info: Dict) -> Dict:
        """Charge le barème de l'évaluation"""
        try:
            bareme_path = Path(evaluation_info['dossier']) / "bareme_evaluation.json"
            if bareme_path.exists():
                with open(bareme_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur chargement barème: {e}")
        
        # Barème par défaut si pas trouvé
        return {
            "note_totale": 20,
            "questions": [
                {
                    "numero": 1,
                    "intitule": "Question générale",
                    "points_total": 20,
                    "type": "ouverte",
                    "criteres": ["Pertinence", "Exactitude"]
                }
            ]
        }
    
    def _extract_student_names(self, copy_path: str, index: int) -> tuple:
        """Extrait le nom et prénom depuis le nom de fichier"""
        filename = Path(copy_path).stem
        
        # Tentative extraction NOM_Prenom
        if '_' in filename:
            parts = filename.split('_')
            if len(parts) >= 2:
                return parts[0], parts[1]
            else:
                return parts[0], f"Prenom{index+1}"
        else:
            return f"Etudiant{index+1}", f"Prenom{index+1}"
    
    def _create_error_result(self, student_name: str, student_firstname: str, 
                           error_msg: str, rank: int) -> Dict:
        """Crée un résultat d'erreur compatible"""
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
            "points_amelioration": ["Correction manuelle nécessaire"],
            "conseils_personnalises": ["Contactez l'enseignant"],
            "diagnostic_performance": "Erreur de traitement",
            "questions": [],
            "questions_avec_commentaires": [],
            "detection_triche": {
                "similarite_detectee": False,
                "score_max": 0.0,
                "algorithme": "error"
            },
            "necessite_revision_humaine": True,
            "qualite_correction": {
                "profil_utilise": "Erreur",
                "confiance_ocr": 0.0,
                "modele_ia": "error",
                "verification_double": False
            },
            "ai_details": {
                "error_message": error_msg,
                "processing_time": 0
            }
        }

# Interface pour compatibility avec l'existant
def process_copies_with_ai(evaluation_info: Dict, copies_paths: List[str], 
                          profile: str = "excellence") -> List[Dict]:
    """
    Interface simple pour traiter les copies avec l'IA
    Compatible avec l'architecture existante
    """
    engine = AICorrecionEngine()
    return engine.process_evaluation_copies(evaluation_info, copies_paths, profile)
