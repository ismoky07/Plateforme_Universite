"""
utils/ai_ocr_processor.py
==========================
Module OCR manuscrit hybride - Combine sophistication du module 1 avec simplicité du module 2
Utilise GPT-4 Vision pour la transcription avancée de copies manuscrites

GUIDE D'UTILISATION :
===================

1. FONCTION PRINCIPALE (objets TranscriptionResult) :
   - transcribe_manuscript_copy() → TranscriptionResult
   - Utiliser quand vous voulez les objets typés

2. FONCTIONS COMPATIBILITÉ (dictionnaires) :
   - transcribe_manuscript_copy_dict() → Dict
   - transcribe_with_analysis() → Dict  
   - batch_transcribe_copies() → Dict
   - Utiliser pour intégration avec systèmes existants

3. FONCTION RAPIDE :
   - quick_transcribe() → str
   - Utiliser pour tests rapides

IMPORTANT : Si vous obtenez l'erreur "'TranscriptionResult' object has no attribute 'get'",
utilisez les fonctions qui retournent des Dict (fonctions avec _dict ou _analysis)
"""

import base64
import time
import re
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from openai import OpenAI
from dotenv import load_dotenv

# ==========================================
# MODÈLES DE DONNÉES
# ==========================================

@dataclass
class TranscriptionResult:
    """Résultat complet de transcription manuscrite"""
    transcribed_text: str
    confidence: float
    quality: str
    processing_time: float
    model_used: str
    pages_processed: int
    word_count: int
    character_count: int
    
    # Analyses avancées du module 1
    matiere: str = "general"
    type_exercice: str = "redaction"
    structure_detectee: Dict = field(default_factory=dict)
    formules_maths: List[Dict] = field(default_factory=list)
    mots_incertains: List[Dict] = field(default_factory=list)
    suggestions_amelioration: List[str] = field(default_factory=list)
    erreurs_transcription: List[str] = field(default_factory=list)
    
    # Métriques détaillées
    qualite_ecriture: str = "INCONNUE"
    confiance_globale: float = 0.0

# ==========================================
# CONFIGURATION ET INITIALISATION
# ==========================================

def init_ocr_client():
    """Initialise le client OpenAI pour OCR"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("Clé API OpenAI manquante dans .env ou environnement")
    
    return OpenAI(api_key=api_key)

def get_quality_config(quality: str) -> Dict:
    """Configuration selon le niveau de qualité"""
    configs = {
        "maximum": {
            "model": "gpt-4o",
            "max_tokens": 4000,
            "temperature": 0.05,
            "detail": "high"
        },
        "high": {
            "model": "gpt-4o",
            "max_tokens": 3000,
            "temperature": 0.1,
            "detail": "high"
        },
        "standard": {
            "model": "gpt-4o",
            "max_tokens": 2000,
            "temperature": 0.15,
            "detail": "auto"
        }
    }
    return configs.get(quality, configs["high"])

# ==========================================
# PROMPTS SPÉCIALISÉS (du module 1)
# ==========================================

def build_specialized_prompt(matiere: str = "general", type_exercice: str = "redaction") -> str:
    """Construit le prompt spécialisé selon la matière"""
    
    base_prompts = {
        "general": """Tu es un expert en lecture d'écriture manuscrite scolaire.

**ÉTAPE 1 - ÉVALUATION DE L'ÉCRITURE**
Évalue la qualité de l'écriture manuscrite :
- EXCELLENTE : Écriture très claire, facilement lisible
- BONNE : Écriture claire avec quelques difficultés mineures  
- MOYENNE : Écriture lisible mais nécessite attention
- DIFFICILE : Écriture peu lisible, nombreuses incertitudes
- ILLISIBLE : Impossible à déchiffrer

**ÉTAPE 2 - TRANSCRIPTION PRÉCISE**
Transcris le texte manuscrit en respectant :
- Orthographe exacte (même si erronée)
- Ponctuation originale
- Structure des paragraphes
- Marque les mots incertains : [INCERTAIN: mot_probable]
- Marque les mots illisibles : [ILLISIBLE]
- Conserve les ratures et corrections : [RATURE: ancien_mot → nouveau_mot]

**ÉTAPE 3 - STRUCTURE DE RÉPONSE**
Identifie la structure :
- Introduction/développement/conclusion
- Listes à puces ou numérotées
- Titres et sous-titres
- Schémas ou dessins : [SCHÉMA: description]""",

        "mathematiques": """Tu es spécialisé en lecture de copies de mathématiques manuscrites.

**ÉTAPE 1 - TRANSCRIPTION MATHÉMATIQUE**
- Formules : utilise notation LaTeX entre $ $
- Équations : une par ligne avec numérotation si présente
- Calculs : respecte la mise en page originale
- Figures géométriques : [FIGURE: description détaillée]
- Graphiques : [GRAPHIQUE: description des axes et courbes]

**ÉTAPE 2 - GESTION DES DIFFICULTÉS**
- Symboles ambigus : [SYMBOLE_INCERTAIN: ≈ ou = ou ≡]
- Chiffres difficiles : [CHIFFRE_INCERTAIN: 6 ou 8]
- Variables manuscrites : [VAR_INCERTAIN: x ou α]

**ÉTAPE 3 - STRUCTURE MATHÉMATIQUE**
Identifie :
- Énoncé du problème
- Hypothèses et données
- Étapes de résolution
- Calculs intermédiaires
- Résultat final
- Vérification/conclusion""",

        "francais": """Tu es expert en copies de français manuscrites.

**ÉTAPE 1 - TRANSCRIPTION LITTÉRAIRE**
- Conserve la ponctuation originale
- Respecte les alinéas et paragraphes
- Note les citations : "texte cité"
- Marque les références : [REF: auteur, œuvre]

**ÉTAPE 2 - STRUCTURE RÉDACTIONNELLE**
Identifie :
- Introduction (accroche, problématique, annonce du plan)
- Développement (parties, sous-parties, transitions)
- Conclusion (synthèse, ouverture)
- Citations et exemples
- Argumentaire et analyses

**ÉTAPE 3 - QUALITÉ RÉDACTIONNELLE**
Note :
- Niveau de langue utilisé
- Richesse du vocabulaire
- Complexité syntaxique
- Cohérence argumentative"""
    }
    
    prompt = base_prompts.get(matiere, base_prompts["general"])
    
    # Adaptation selon le type d'exercice
    if type_exercice == "qcm":
        prompt += """

**SPÉCIFICITÉ QCM :**
- Identifie les questions numérotées
- Repère les réponses cochées : [COCHÉ: A] [NON_COCHÉ: B,C,D]
- Note les hésitations : [RATURE: A → C]"""
    
    # Format de réponse unifié
    prompt += """

**FORMAT DE RÉPONSE OBLIGATOIRE :**
```
QUALITÉ_ÉCRITURE: [EXCELLENTE/BONNE/MOYENNE/DIFFICILE/ILLISIBLE]
CONFIANCE_TRANSCRIPTION: [0-100]%

TEXTE_TRANSCRIT:
[Transcription complète du texte]

STRUCTURE_DÉTECTÉE:
- Type: [dissertation/exercice/qcm/autre]
- Parties: [liste des sections identifiées]
- Organisation: [description de la structure]

MOTS_INCERTAINS:
- [Liste des mots difficiles à lire]

FORMULES_DÉTECTÉES:
- [Liste des formules mathématiques si applicable]

OBSERVATIONS:
- [Notes sur difficultés rencontrées]
- [Suggestions pour améliorer la lisibilité]
```

Analyse maintenant cette copie manuscrite :"""
    
    return prompt

# ==========================================
# FONCTIONS PRINCIPALES
# ==========================================

def transcribe_manuscript_copy_dict(client, copy_path: str, quality: str = "high", 
                                  matiere: str = "general", type_exercice: str = "redaction") -> Dict[str, Any]:
    """
    Version dictionnaire de transcribe_manuscript_copy pour compatibilité
    Retourne un dictionnaire au lieu d'un TranscriptionResult
    """
    result = transcribe_manuscript_copy(client, copy_path, quality, matiere, type_exercice)
    return transcription_result_to_dict(result)

def transcribe_manuscript_copy(client, copy_path: str, quality: str = "high", 
                             matiere: str = "general", type_exercice: str = "redaction") -> TranscriptionResult:
    """
    Transcrit une copie manuscrite avec analyse sophistiquée
    
    Args:
        client: Client OpenAI
        copy_path: Chemin vers la copie (PDF ou image)
        quality: Niveau de qualité ("maximum", "high", "standard")
        matiere: Matière scolaire ("general", "mathematiques", "francais")
        type_exercice: Type d'exercice ("redaction", "qcm", "dissertation")
    
    Returns:
        TranscriptionResult avec analyse complète
    """
    
    start_time = time.time()
    
    try:
        config = get_quality_config(quality)
        
        # Traitement du fichier
        if copy_path.lower().endswith('.pdf'):
            images_paths = convert_pdf_to_images(copy_path)
            all_transcriptions = []
            
            for img_path in images_paths:
                page_result = _transcribe_single_image(client, img_path, config, matiere, type_exercice)
                all_transcriptions.append(page_result)
            
            # Fusionner les résultats multi-pages
            merged_result = _merge_page_results(all_transcriptions)
            pages_count = len(images_paths)
            
            # Nettoyage
            cleanup_temp_images(copy_path)
            
        else:
            # Image unique
            merged_result = _transcribe_single_image(client, copy_path, config, matiere, type_exercice)
            pages_count = 1
        
        # Calculs finaux
        processing_time = time.time() - start_time
        
        # Créer le résultat final
        result = TranscriptionResult(
            transcribed_text=merged_result.get('texte_transcrit', ''),
            confidence=merged_result.get('confiance_globale', 0.0),
            quality=_assess_writing_quality(merged_result),
            processing_time=round(processing_time, 2),
            model_used=config["model"],
            pages_processed=pages_count,
            word_count=len(merged_result.get('texte_transcrit', '').split()),
            character_count=len(merged_result.get('texte_transcrit', '')),
            
            # Analyses avancées
            matiere=matiere,
            type_exercice=type_exercice,
            structure_detectee=merged_result.get('structure_detectee', {}),
            formules_maths=merged_result.get('formules_maths', []),
            mots_incertains=merged_result.get('mots_incertains', []),
            suggestions_amelioration=merged_result.get('suggestions_amelioration', []),
            erreurs_transcription=merged_result.get('erreurs_transcription', []),
            qualite_ecriture=merged_result.get('qualite_ecriture', 'INCONNUE'),
            confiance_globale=merged_result.get('confiance_globale', 0.0)
        )
        
        return result
        
    except Exception as e:
        return TranscriptionResult(
            transcribed_text=f"[ERREUR TRANSCRIPTION: {str(e)}]",
            confidence=0.0,
            quality="error",
            processing_time=time.time() - start_time,
            model_used="error",
            pages_processed=0,
            word_count=0,
            character_count=0,
            erreurs_transcription=[str(e)]
        )

def _transcribe_single_image(client, image_path: str, config: Dict, 
                           matiere: str, type_exercice: str) -> Dict:
    """Transcrit une seule image avec analyse sophistiquée"""
    
    try:
        # Encoder l'image
        base64_image = encode_image_to_base64(image_path)
        
        # Construire le prompt spécialisé
        prompt = build_specialized_prompt(matiere, type_exercice)
        
        # Appel API
        response = client.chat.completions.create(
            model=config["model"],
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
                                "detail": config["detail"]
                            }
                        }
                    ]
                }
            ],
            max_tokens=config["max_tokens"],
            temperature=config["temperature"]
        )
        
        response_text = response.choices[0].message.content
        
        # Parser la réponse avec analyse sophistiquée
        return _parse_sophisticated_response(response_text)
        
    except Exception as e:
        return {
            'texte_transcrit': f"[ERREUR: {str(e)}]",
            'qualite_ecriture': 'ERREUR',
            'confiance_globale': 0.0,
            'erreurs_transcription': [str(e)]
        }

def _parse_sophisticated_response(response_text: str) -> Dict:
    """Parse la réponse GPT avec extraction sophistiquée"""
    
    result = {
        'texte_transcrit': "",
        'qualite_ecriture': "INCONNUE",
        'confiance_globale': 0.0,
        'mots_incertains': [],
        'structure_detectee': {},
        'formules_maths': [],
        'erreurs_transcription': [],
        'suggestions_amelioration': []
    }
    
    try:
        lines = response_text.split('\n')
        current_section = None
        texte_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('QUALITÉ_ÉCRITURE:'):
                result['qualite_ecriture'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('CONFIANCE_TRANSCRIPTION:'):
                confiance_str = line.split(':', 1)[1].strip().replace('%', '')
                try:
                    result['confiance_globale'] = float(confiance_str)
                except:
                    result['confiance_globale'] = 50.0
            
            elif line == 'TEXTE_TRANSCRIT:':
                current_section = 'texte'
            
            elif line == 'STRUCTURE_DÉTECTÉE:':
                current_section = 'structure'
                if texte_lines:
                    result['texte_transcrit'] = '\n'.join(texte_lines)
                    texte_lines = []
            
            elif line == 'MOTS_INCERTAINS:':
                current_section = 'incertains'
            
            elif line == 'FORMULES_DÉTECTÉES:':
                current_section = 'formules'
            
            elif line == 'OBSERVATIONS:':
                current_section = 'observations'
            
            elif line and not line.startswith('```'):
                if current_section == 'texte':
                    texte_lines.append(line)
                elif current_section == 'incertains' and line.startswith('- '):
                    result['mots_incertains'].append({
                        'mot': line[2:].strip(),
                        'confiance': 'faible'
                    })
                elif current_section == 'formules' and line.startswith('- '):
                    result['formules_maths'].append({
                        'contenu': line[2:].strip(),
                        'type': 'detectee'
                    })
                elif current_section == 'observations' and line.startswith('- '):
                    suggestion = line[2:].strip()
                    if any(keyword in suggestion.lower() for keyword in ['améliorer', 'conseil', 'recommand']):
                        result['suggestions_amelioration'].append(suggestion)
        
        # Finaliser le texte
        if texte_lines:
            result['texte_transcrit'] = '\n'.join(texte_lines)
        
        # Analyse complémentaire du texte
        if result['texte_transcrit']:
            result['structure_detectee'] = _analyze_text_structure(result['texte_transcrit'])
            result['mots_incertains'].extend(_extract_uncertain_words(result['texte_transcrit']))
            result['formules_maths'].extend(_extract_math_formulas(result['texte_transcrit']))
        
        return result
        
    except Exception as e:
        result['erreurs_transcription'].append(f"Erreur parsing: {str(e)}")
        return result

# ==========================================
# ANALYSES SOPHISTIQUÉES
# ==========================================

def _analyze_text_structure(text: str) -> Dict:
    """Analyse la structure du texte"""
    
    structure = {
        'type_detecte': 'redaction',
        'parties': [],
        'organisation': 'lineaire',
        'elements_detectes': []
    }
    
    lines = text.split('\n')
    partie_courante = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Détecter les titres
        if _is_title(line):
            partie_courante = {
                'titre': line,
                'position': i,
                'type': 'titre'
            }
            structure['parties'].append(partie_courante)
            structure['elements_detectes'].append(f"Titre: {line}")
        
        # Détecter les listes
        elif _is_list_item(line):
            structure['elements_detectes'].append(f"Liste: {line[:30]}...")
            structure['organisation'] = 'structuree'
    
    if len(structure['parties']) >= 3:
        structure['organisation'] = 'bien_structuree'
    
    return structure

def _extract_uncertain_words(text: str) -> List[Dict]:
    """Extrait les mots incertains du texte"""
    
    words = []
    patterns = [
        r'\[INCERTAIN:\s*([^\]]+)\]',
        r'\[ILLISIBLE\]',
        r'\[RATURE:\s*([^\]]+)\]'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            words.append({
                'mot': match.group(1) if match.groups() else 'ILLISIBLE',
                'confiance': 'faible',
                'type': 'incertain'
            })
    
    return words

def _extract_math_formulas(text: str) -> List[Dict]:
    """Extrait les formules mathématiques"""
    
    formulas = []
    patterns = [
        r'\$[^$]+\$',  # LaTeX
        r'\[FORMULE:\s*([^\]]+)\]',  # Formules marquées
        r'[a-zA-Z]\s*[=≈≠<>≤≥]\s*[0-9a-zA-Z\+\-\*/\(\)]+',  # Équations
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            formulas.append({
                'contenu': match.group(),
                'type': 'mathematique',
                'confiance': 'haute' if '$' in match.group() else 'moyenne'
            })
    
    return formulas

def _is_title(line: str) -> bool:
    """Détecte si une ligne est un titre"""
    return (len(line) < 100 and 
            (line.isupper() or 
             line.startswith(('I.', 'II.', 'III.', '1.', '2.', '3.')) or
             line.endswith(':') or
             any(word in line.lower() for word in ['introduction', 'conclusion', 'partie'])))

def _is_list_item(line: str) -> bool:
    """Détecte si une ligne est un élément de liste"""
    return (line.startswith(('- ', '• ', '* ')) or
            re.match(r'^\d+[\.\)]\s', line) or
            re.match(r'^[a-zA-Z][\.\)]\s', line))

def _assess_writing_quality(result: Union[Dict, TranscriptionResult]) -> str:
    """Évalue la qualité globale"""
    
    # Gestion des deux types d'objets avec fonction utilitaire
    qualite = _safe_get_attribute(result, 'qualite_ecriture', 'INCONNUE')
    confiance = _safe_get_attribute(result, 'confiance_globale', 0.0)
    
    if qualite == 'EXCELLENTE' and confiance >= 80:
        return 'excellent'
    elif qualite in ['BONNE', 'EXCELLENTE'] and confiance >= 60:
        return 'good'
    elif qualite in ['MOYENNE', 'BONNE'] and confiance >= 40:
        return 'average'
    elif qualite == 'DIFFICILE' or confiance < 40:
        return 'difficult'
    else:
        return 'unknown'

def _merge_page_results(results: List[Dict]) -> Dict:
    """Fusionne les résultats de plusieurs pages"""
    
    merged = {
        'texte_transcrit': '',
        'qualite_ecriture': 'MOYENNE',
        'confiance_globale': 0.0,
        'mots_incertains': [],
        'structure_detectee': {},
        'formules_maths': [],
        'erreurs_transcription': [],
        'suggestions_amelioration': []
    }
    
    if not results:
        return merged
    
    # Fusionner les textes
    textes = []
    for i, result in enumerate(results):
        texte = result.get('texte_transcrit', '')
        if texte:
            textes.append(f"=== PAGE {i+1} ===\n{texte}")
    
    merged['texte_transcrit'] = '\n\n'.join(textes)
    
    # Moyenner la confiance
    confidences = [r.get('confiance_globale', 0.0) for r in results if r.get('confiance_globale')]
    if confidences:
        merged['confiance_globale'] = sum(confidences) / len(confidences)
    
    # Déterminer la qualité globale
    qualites = [r.get('qualite_ecriture', 'INCONNUE') for r in results]
    if 'EXCELLENTE' in qualites:
        merged['qualite_ecriture'] = 'EXCELLENTE'
    elif 'BONNE' in qualites:
        merged['qualite_ecriture'] = 'BONNE'
    elif 'MOYENNE' in qualites:
        merged['qualite_ecriture'] = 'MOYENNE'
    else:
        merged['qualite_ecriture'] = 'DIFFICILE'
    
    # Fusionner les listes
    for result in results:
        merged['mots_incertains'].extend(result.get('mots_incertains', []))
        merged['formules_maths'].extend(result.get('formules_maths', []))
        merged['erreurs_transcription'].extend(result.get('erreurs_transcription', []))
        merged['suggestions_amelioration'].extend(result.get('suggestions_amelioration', []))
    
    return merged

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def _safe_get_attribute(obj: Union[Dict, Any], attr_name: str, default: Any = None) -> Any:
    """Récupère un attribut de manière sécurisée depuis un dict ou un objet"""
    if isinstance(obj, dict):
        return obj.get(attr_name, default)
    else:
        return getattr(obj, attr_name, default)

def encode_image_to_base64(image_path: str) -> str:
    """Encode une image en base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise Exception(f"Erreur encodage image: {str(e)}")

def convert_pdf_to_images(pdf_path: str) -> List[str]:
    """Convertit un PDF en images"""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        images_paths = []
        
        output_dir = Path(pdf_path).parent / "temp_images"
        output_dir.mkdir(exist_ok=True)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            zoom = 2.0  # Haute résolution
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img_path = output_dir / f"page_{page_num + 1}.png"
            pix.save(str(img_path))
            images_paths.append(str(img_path))
            
            pix = None
        
        doc.close()
        return images_paths
        
    except ImportError:
        raise Exception("PyMuPDF non installé. Installez avec: pip install PyMuPDF")
    except Exception as e:
        raise Exception(f"Erreur conversion PDF: {str(e)}")

def cleanup_temp_images(pdf_path: str):
    """Nettoie les images temporaires"""
    try:
        import shutil
        temp_dir = Path(pdf_path).parent / "temp_images"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    except:
        pass

# ==========================================
# INTERFACES SIMPLIFIÉES
# ==========================================

def quick_transcribe(client, copy_path: str, matiere: str = "general") -> str:
    """Transcription rapide pour tests"""
    result = transcribe_manuscript_copy(client, copy_path, quality="standard", matiere=matiere)
    return result.transcribed_text

def transcription_result_to_dict(result: TranscriptionResult) -> Dict[str, Any]:
    """Convertit un TranscriptionResult en dictionnaire pour compatibilité"""
    return {
        "transcribed_text": result.transcribed_text,
        "confidence": result.confidence,
        "quality": result.quality,
        "processing_time": result.processing_time,
        "model_used": result.model_used,
        "pages_processed": result.pages_processed,
        "word_count": result.word_count,
        "character_count": result.character_count,
        "matiere": result.matiere,
        "type_exercice": result.type_exercice,
        "structure_detectee": result.structure_detectee,
        "formules_maths": result.formules_maths,
        "mots_incertains": result.mots_incertains,
        "suggestions_amelioration": result.suggestions_amelioration,
        "qualite_ecriture": result.qualite_ecriture,
        "confiance_globale": result.confiance_globale,
        "erreurs_transcription": result.erreurs_transcription
    }

def transcribe_with_analysis(client, copy_path: str, matiere: str = "general", 
                           type_exercice: str = "redaction") -> Dict[str, Any]:
    """Transcription avec analyse complète - format dict pour compatibilité"""
    result = transcribe_manuscript_copy(client, copy_path, quality="high", 
                                      matiere=matiere, type_exercice=type_exercice)
    
    # Conversion en dict pour compatibilité
    return transcription_result_to_dict(result)

def batch_transcribe_copies(client, copy_paths: List[str], matiere: str = "general") -> Dict[str, Any]:
    """Traite plusieurs copies avec statistiques globales"""
    
    results = {
        'transcriptions': {},
        'statistiques': {
            'total_copies': len(copy_paths),
            'copies_excellentes': 0,
            'copies_bonnes': 0,
            'copies_moyennes': 0,
            'copies_difficiles': 0,
            'mots_incertains_total': 0,
            'confiance_moyenne': 0.0
        }
    }
    
    confidences = []
    
    for copy_path in copy_paths:
        try:
            result = transcribe_manuscript_copy(client, copy_path, matiere=matiere)
            
            # Convertir en dict pour compatibilité
            result_dict = transcription_result_to_dict(result)
            results['transcriptions'][copy_path] = result_dict
            
            # Mise à jour des statistiques
            if result.quality == 'excellent':
                results['statistiques']['copies_excellentes'] += 1
            elif result.quality == 'good':
                results['statistiques']['copies_bonnes'] += 1
            elif result.quality == 'average':
                results['statistiques']['copies_moyennes'] += 1
            else:
                results['statistiques']['copies_difficiles'] += 1
            
            results['statistiques']['mots_incertains_total'] += len(result.mots_incertains)
            confidences.append(result.confidence)
            
        except Exception as e:
            print(f"Erreur traitement {copy_path}: {str(e)}")
            # Ajouter un résultat d'erreur sous forme de dict
            results['transcriptions'][copy_path] = {
                "transcribed_text": f"[ERREUR: {str(e)}]",
                "confidence": 0.0,
                "quality": "error",
                "processing_time": 0.0,
                "model_used": "error",
                "pages_processed": 0,
                "word_count": 0,
                "character_count": 0,
                "matiere": matiere,
                "type_exercice": "redaction",
                "structure_detectee": {},
                "formules_maths": [],
                "mots_incertains": [],
                "suggestions_amelioration": [],
                "qualite_ecriture": "ERREUR",
                "confiance_globale": 0.0,
                "erreurs_transcription": [str(e)]
            }
    
    # Confiance moyenne
    if confidences:
        results['statistiques']['confiance_moyenne'] = sum(confidences) / len(confidences)
    
    return results