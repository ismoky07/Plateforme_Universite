#!/usr/bin/env python3
"""
Utilitaires consolidés pour le système de correction d'épreuves manuscrites
==========================================================================

Fonctions utilitaires communes pour :
- Gestion sécurisée des textes et encodages
- Système de logging adapté
- Validation et nettoyage des données
- Fonctions helper pour l'OCR et la correction
- Gestion des erreurs et exceptions
- Fonctions de traitement d'images et PDF
- Utilitaires pour barèmes et corrections

Consolidé depuis tous les modules du système.
"""

import os
import sys
import io
import re
import json
import base64
import unicodedata
import tempfile
import time
from typing import Optional, Union, List, Dict, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime

# ============================================
# CONFIGURATION GLOBALE
# ============================================

# Configuration de l'encodage pour éviter les problèmes
try:
    if not hasattr(sys.stdout, 'buffer') or not sys.stdout.__class__.__name__ == 'OutStream':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='backslashreplace')
except Exception:
    pass

# Configuration du logger global
LOGGER_NAME = "correction_agent"
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(asctime)s] %(levelname)s - %(message)s'

# ============================================
# SYSTÈME DE LOGGING SÉCURISÉ
# ============================================

def init_logger(log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Initialise le système de logging pour la correction
    
    Args:
        log_file: Fichier de log (optionnel)
        level: Niveau de log
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(LOGGER_NAME)
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier si spécifié
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Impossible de créer le fichier de log {log_file}: {e}")
    
    return logger

def safe_print(message: str, level: str = "INFO", logger_name: str = None):
    """
    Fonction de logging sécurisée pour le système de correction
    
    Args:
        message: Message à afficher/logger
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Nom du logger (optionnel)
    """
    try:
        # Nettoyer le message
        clean_message = safe_text_handling(str(message))
        
        # Obtenir le logger
        logger = logging.getLogger(logger_name or LOGGER_NAME)
        
        # Si pas de handlers, configuration basique
        if not logger.handlers:
            logger = init_logger()
        
        # Logger selon le niveau
        level_upper = level.upper()
        if level_upper == "DEBUG":
            logger.debug(clean_message)
        elif level_upper == "WARNING":
            logger.warning(clean_message)
        elif level_upper == "ERROR":
            logger.error(clean_message)
        elif level_upper == "CRITICAL":
            logger.critical(clean_message)
        else:
            logger.info(clean_message)
            
        # Aussi afficher en console si pas en mode silencieux
        if not os.getenv('CORRECTION_SILENT_MODE'):
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {clean_message}")
            except:
                # Fallback ultime
                sys.stdout.write(f"{clean_message}\n")
                sys.stdout.flush()
                
    except Exception:
        # Fallback d'urgence si même le logging échoue
        try:
            sys.stdout.write(f"[SAFE_PRINT] {message}\n")
            sys.stdout.flush()
        except:
            pass

# ============================================
# GESTION SÉCURISÉE DU TEXTE
# ============================================

def safe_text_handling(text: Union[str, bytes, None]) -> str:
    """
    Assure une gestion sécurisée du texte avec encodage UTF-8
    
    Args:
        text: Texte à traiter (str, bytes ou None)
    
    Returns:
        Texte proprement encodé en UTF-8
    """
    if text is None:
        return ""
    
    try:
        # Si c'est déjà une chaîne
        if isinstance(text, str):
            # Normaliser les caractères Unicode
            text = unicodedata.normalize('NFKC', text)
            return text
        
        # Si c'est des bytes
        elif isinstance(text, bytes):
            # Essayer différents encodages
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    decoded = text.decode(encoding)
                    return unicodedata.normalize('NFKC', decoded)
                except UnicodeDecodeError:
                    continue
            
            # Fallback avec remplacement d'erreurs
            return text.decode('utf-8', errors='replace')
        
        # Autres types
        else:
            return unicodedata.normalize('NFKC', str(text))
    
    except Exception:
        # Fallback ultime
        return str(text) if text is not None else ""

def nettoyer_texte_ocr(text: str) -> str:
    """
    Nettoie un texte issu de l'OCR pour améliorer la qualité
    
    Args:
        text: Texte brut de l'OCR
    
    Returns:
        Texte nettoyé
    """
    if not text:
        return ""
    
    text = safe_text_handling(text)
    
    # Remplacer les caractères problématiques communs en OCR
    replacements = {
        'œ': 'oe',  # Souvent mal reconnu
        'æ': 'ae',
        '«': '"',   # Guillemets
        '»': '"',
        ''': "'",   # Apostrophes
        ''': "'",
        '"': '"',
        '"': '"',
        '…': '...',
        '–': '-',   # Tirets
        '—': '-',
        '\u00A0': ' ',  # Espace insécable
        '\u2009': ' ',  # Espace fine
        '\u200B': '',   # Espace de largeur nulle
    }
    
    for ancien, nouveau in replacements.items():
        text = text.replace(ancien, nouveau)
    
    # Nettoyer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    # Nettoyer les retours à la ligne multiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

def extraire_mots_cles(text: str, min_length: int = 3, max_words: int = 20) -> List[str]:
    """
    Extrait les mots-clés importants d'un texte
    
    Args:
        text: Texte à analyser
        min_length: Longueur minimale des mots
        max_words: Nombre maximum de mots-clés
    
    Returns:
        Liste des mots-clés extraits
    """
    if not text:
        return []
    
    text = safe_text_handling(text).lower()
    
    # Mots vides français (stop words)
    mots_vides = {
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'mais', 'donc', 'or',
        'ni', 'car', 'ce', 'ces', 'cette', 'cet', 'dans', 'sur', 'avec', 'sans', 'pour',
        'par', 'vers', 'chez', 'sous', 'entre', 'que', 'qui', 'quoi', 'dont', 'où', 'quand',
        'comment', 'pourquoi', 'si', 'comme', 'très', 'plus', 'moins', 'aussi', 'tant',
        'bien', 'mal', 'mieux', 'encore', 'déjà', 'toujours', 'jamais', 'souvent', 'parfois',
        'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'je', 'tu', 'me', 'te', 'se',
        'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'notre', 'votre', 'leur',
        'est', 'était', 'sera', 'être', 'avoir', 'a', 'ai', 'as', 'avait', 'aura', 'fait',
        'faire', 'dit', 'dire', 'va', 'aller', 'vient', 'venir', 'peut', 'pouvoir'
    }
    
    # Extraire les mots
    mots = re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', text)
    
    # Filtrer et compter
    from collections import Counter
    mots_filtres = [
        mot for mot in mots 
        if len(mot) >= min_length and mot.lower() not in mots_vides
    ]
    
    # Compter les occurrences
    compteur = Counter(mots_filtres)
    
    # Retourner les plus fréquents
    return [mot for mot, _ in compteur.most_common(max_words)]

def detecter_langue(text: str) -> str:
    """
    Détecte la langue d'un texte (basique)
    
    Args:
        text: Texte à analyser
    
    Returns:
        Code de langue ('fr', 'en', 'es', etc.)
    """
    if not text:
        return 'fr'  # Défaut français
    
    text_lower = safe_text_handling(text).lower()
    
    # Mots indicateurs par langue
    indicateurs = {
        'fr': ['le', 'la', 'les', 'de', 'et', 'que', 'est', 'dans', 'avec', 'pour', 'être', 'avoir'],
        'en': ['the', 'and', 'of', 'to', 'in', 'is', 'with', 'for', 'as', 'are', 'was', 'will'],
        'es': ['el', 'la', 'de', 'que', 'en', 'y', 'con', 'por', 'para', 'es', 'del', 'los'],
        'it': ['il', 'di', 'che', 'la', 'in', 'e', 'con', 'per', 'da', 'su', 'un', 'del'],
        'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf']
    }
    
    scores = {}
    mots_text = re.findall(r'\b\w+\b', text_lower)
    
    for langue, mots_indicateurs in indicateurs.items():
        score = sum(1 for mot in mots_text if mot in mots_indicateurs)
        scores[langue] = score
    
    # Retourner la langue avec le meilleur score
    return max(scores.items(), key=lambda x: x[1])[0] if scores else 'fr'

def normaliser_texte_pour_comparaison(text: str) -> str:
    """
    Normalise un texte pour faciliter les comparaisons
    
    Args:
        text: Texte à normaliser
    
    Returns:
        Texte normalisé
    """
    if not text:
        return ""
    
    text = safe_text_handling(text)
    
    # Convertir en minuscules
    text = text.lower()
    
    # Supprimer les accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Supprimer la ponctuation et espaces multiples
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def calculer_similarite_textuelle(text1: str, text2: str) -> float:
    """
    Calcule la similarité entre deux textes (0-1)
    
    Args:
        text1: Premier texte
        text2: Deuxième texte
    
    Returns:
        Score de similarité entre 0 et 1
    """
    if not text1 or not text2:
        return 0.0
    
    try:
        from difflib import SequenceMatcher
        
        # Normaliser les textes
        norm1 = normaliser_texte_pour_comparaison(text1)
        norm2 = normaliser_texte_pour_comparaison(text2)
        
        # Calculer la similarité
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    except ImportError:
        # Fallback basique si difflib n'est pas disponible
        mots1 = set(normaliser_texte_pour_comparaison(text1).split())
        mots2 = set(normaliser_texte_pour_comparaison(text2).split())
        
        if not mots1 or not mots2:
            return 0.0
        
        intersection = len(mots1.intersection(mots2))
        union = len(mots1.union(mots2))
        
        return intersection / union if union > 0 else 0.0

def extraire_nombres_du_texte(text: str) -> List[float]:
    """
    Extrait tous les nombres d'un texte
    
    Args:
        text: Texte à analyser
    
    Returns:
        Liste des nombres trouvés
    """
    if not text:
        return []
    
    # Patterns pour différents formats de nombres
    patterns = [
        r'\b\d+[.,]\d+\b',  # Nombres décimaux
        r'\b\d+\b',         # Nombres entiers
        r'\b\d+/\d+\b'      # Fractions
    ]
    
    nombres = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                # Normaliser les séparateurs décimaux
                nombre_str = match.replace(',', '.')
                
                # Gérer les fractions
                if '/' in nombre_str:
                    parts = nombre_str.split('/')
                    if len(parts) == 2:
                        nombre = float(parts[0]) / float(parts[1])
                else:
                    nombre = float(nombre_str)
                
                nombres.append(nombre)
            except ValueError:
                continue
    
    return nombres

# ============================================
# VALIDATION ET NETTOYAGE DES DONNÉES
# ============================================

def valider_chemin_fichier(chemin: Union[str, Path], extensions_acceptees: List[str] = None) -> Dict[str, Any]:
    """
    Valide un chemin de fichier
    
    Args:
        chemin: Chemin à valider
        extensions_acceptees: Liste des extensions acceptées
    
    Returns:
        Dict avec le résultat de validation
    """
    resultat = {
        'valide': False,
        'chemin_absolu': '',
        'extension': '',
        'taille': 0,
        'erreurs': [],
        'avertissements': []
    }
    
    try:
        chemin_path = Path(chemin)
        resultat['chemin_absolu'] = str(chemin_path.absolute())
        resultat['extension'] = chemin_path.suffix.lower()
        
        # Vérifier existence
        if not chemin_path.exists():
            resultat['erreurs'].append(f"Fichier inexistant: {chemin}")
            return resultat
        
        # Vérifier que c'est un fichier
        if not chemin_path.is_file():
            resultat['erreurs'].append(f"N'est pas un fichier: {chemin}")
            return resultat
        
        # Vérifier extension
        if extensions_acceptees and resultat['extension'] not in extensions_acceptees:
            resultat['erreurs'].append(f"Extension non acceptée: {resultat['extension']}")
            return resultat
        
        # Taille du fichier
        resultat['taille'] = chemin_path.stat().st_size
        
        # Avertissements
        if resultat['taille'] == 0:
            resultat['avertissements'].append("Fichier vide")
        elif resultat['taille'] > 50 * 1024 * 1024:  # 50MB
            resultat['avertissements'].append("Fichier très volumineux")
        
        resultat['valide'] = True
        
    except Exception as e:
        resultat['erreurs'].append(f"Erreur validation: {str(e)}")
    
    return resultat

def valider_configuration(config: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide une configuration selon un schéma
    
    Args:
        config: Configuration à valider
        schema: Schéma de validation
    
    Returns:
        Dict avec le résultat de validation
    """
    resultat = {
        'valide': True,
        'erreurs': [],
        'avertissements': [],
        'config_corrigee': config.copy()
    }
    
    try:
        for cle, spec in schema.items():
            valeur = config.get(cle)
            
            # Vérifier champs requis
            if spec.get('required', False) and valeur is None:
                resultat['erreurs'].append(f"Champ requis manquant: {cle}")
                resultat['valide'] = False
                continue
            
            # Appliquer valeur par défaut
            if valeur is None and 'default' in spec:
                resultat['config_corrigee'][cle] = spec['default']
                resultat['avertissements'].append(f"Valeur par défaut appliquée pour {cle}")
                continue
            
            if valeur is not None:
                # Vérifier le type
                type_attendu = spec.get('type')
                if type_attendu and not isinstance(valeur, type_attendu):
                    resultat['erreurs'].append(f"Type incorrect pour {cle}: attendu {type_attendu.__name__}")
                    resultat['valide'] = False
                
                # Vérifier les choix
                choix = spec.get('choices')
                if choix and valeur not in choix:
                    resultat['erreurs'].append(f"Valeur non autorisée pour {cle}: {valeur}")
                    resultat['valide'] = False
                
                # Vérifier les limites
                min_val = spec.get('min')
                max_val = spec.get('max')
                if min_val is not None and isinstance(valeur, (int, float)) and valeur < min_val:
                    resultat['erreurs'].append(f"Valeur trop petite pour {cle}: {valeur} < {min_val}")
                    resultat['valide'] = False
                if max_val is not None and isinstance(valeur, (int, float)) and valeur > max_val:
                    resultat['erreurs'].append(f"Valeur trop grande pour {cle}: {valeur} > {max_val}")
                    resultat['valide'] = False
    
    except Exception as e:
        resultat['erreurs'].append(f"Erreur validation configuration: {str(e)}")
        resultat['valide'] = False
    
    return resultat

# ============================================
# GESTION DES ERREURS ET EXCEPTIONS
# ============================================

def gestion_erreur_robuste(func):
    """
    Décorateur pour gestion robuste des erreurs
    
    Args:
        func: Fonction à décorer
    
    Returns:
        Fonction décorée avec gestion d'erreurs
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            safe_print(f"Erreur dans {func.__name__}: {str(e)}", "ERROR")
            return None
    
    return wrapper

def creer_rapport_erreur(exception: Exception, contexte: str = "") -> Dict[str, Any]:
    """
    Crée un rapport d'erreur détaillé
    
    Args:
        exception: Exception capturée
        contexte: Contexte de l'erreur
    
    Returns:
        Dict avec les détails de l'erreur
    """
    import traceback
    
    return {
        'type_erreur': type(exception).__name__,
        'message': str(exception),
        'contexte': contexte,
        'timestamp': datetime.now().isoformat(),
        'traceback': traceback.format_exc(),
        'suggestions': _generer_suggestions_erreur(exception)
    }

def _generer_suggestions_erreur(exception: Exception) -> List[str]:
    """Génère des suggestions basées sur le type d'erreur"""
    suggestions = []
    
    if isinstance(exception, FileNotFoundError):
        suggestions.append("Vérifier que le chemin du fichier est correct")
        suggestions.append("S'assurer que le fichier existe")
    
    elif isinstance(exception, PermissionError):
        suggestions.append("Vérifier les permissions d'accès au fichier")
        suggestions.append("Exécuter avec des privilèges administrateur si nécessaire")
    
    elif isinstance(exception, ValueError):
        suggestions.append("Vérifier le format des données d'entrée")
        suggestions.append("S'assurer que les valeurs sont dans les plages attendues")
    
    elif isinstance(exception, ConnectionError):
        suggestions.append("Vérifier la connexion internet")
        suggestions.append("Contrôler la validité de la clé API")
    
    elif isinstance(exception, UnicodeDecodeError):
        suggestions.append("Vérifier l'encodage du fichier")
        suggestions.append("Essayer avec un autre format de fichier")
    
    else:
        suggestions.append("Consulter la documentation")
        suggestions.append("Vérifier les logs pour plus de détails")
    
    return suggestions

# ============================================
# FONCTIONS DE FORMATAGE ET CONVERSION
# ============================================

def formater_note(note: float, note_max: float, precision: int = 1, 
                 format_type: str = "decimal") -> str:
    """
    Formate une note selon différents formats
    
    Args:
        note: Note obtenue
        note_max: Note maximale
        precision: Nombre de décimales
        format_type: Type de format ('decimal', 'fraction', 'pourcentage')
    
    Returns:
        Note formatée
    """
    try:
        if format_type == "fraction":
            return f"{note:.{precision}f}/{note_max:.{precision}f}"
        
        elif format_type == "pourcentage":
            pourcentage = (note / note_max) * 100 if note_max > 0 else 0
            return f"{pourcentage:.{precision}f}%"
        
        else:  # decimal par défaut
            return f"{note:.{precision}f}"
    
    except Exception:
        return str(note)

def convertir_dict_en_json_safe(data: Dict[str, Any]) -> str:
    """
    Convertit un dictionnaire en JSON en gérant les types non-sérialisables
    
    Args:
        data: Dictionnaire à convertir
    
    Returns:
        Chaîne JSON
    """
    def serializer(obj):
        """Sérialiseur personnalisé pour les objets non-JSON"""
        if hasattr(obj, 'isoformat'):  # datetime
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # Objets avec attributs
            return obj.__dict__
        elif hasattr(obj, 'dict'):  # Objets Pydantic
            return obj.dict()
        else:
            return str(obj)
    
    try:
        return json.dumps(data, ensure_ascii=False, indent=2, default=serializer)
    except Exception as e:
        safe_print(f"Erreur conversion JSON: {e}", "WARNING")
        return json.dumps({"erreur": "Conversion JSON échouée", "data": str(data)})

def generer_nom_fichier_unique(base_name: str, extension: str = "", 
                              timestamp: bool = True) -> str:
    """
    Génère un nom de fichier unique
    
    Args:
        base_name: Nom de base
        extension: Extension (avec ou sans point)
        timestamp: Ajouter un timestamp
    
    Returns:
        Nom de fichier unique
    """
    # Nettoyer le nom de base
    base_clean = re.sub(r'[^\w\-_]', '_', base_name)
    
    # Normaliser l'extension
    if extension and not extension.startswith('.'):
        extension = f".{extension}"
    
    # Ajouter timestamp si demandé
    if timestamp:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_clean}_{ts}{extension}"
    else:
        return f"{base_clean}{extension}"

# ============================================
# UTILITAIRES POUR IMAGES ET OCR (consolidé depuis ocr_manuscrit.py)
# ============================================

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Encode une image en base64 pour l'API Vision"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        safe_print(f"❌ Erreur encodage {image_path}: {str(e)}")
        return None

def extraire_mots_incertains(texte: str) -> List[Dict]:
    """Extrait les mots marqués comme incertains dans le texte"""
    mots = []
    
    # Pattern pour [INCERTAIN: mot]
    pattern_incertain = r'\[INCERTAIN:\s*([^\]]+)\]'
    matches = re.finditer(pattern_incertain, texte)
    
    for match in matches:
        mots.append({
            'mot': match.group(1).strip(),
            'confiance': 'faible',
            'type': 'incertain'
        })
    
    # Pattern pour [ILLISIBLE]
    pattern_illisible = r'\[ILLISIBLE\]'
    illisibles = len(re.findall(pattern_illisible, texte))
    
    for i in range(illisibles):
        mots.append({
            'mot': '[ILLISIBLE]',
            'confiance': 'nulle',
            'type': 'illisible'
        })
    
    return mots

def est_titre(line: str) -> bool:
    """Détermine si une ligne est un titre"""
    line = line.strip()
    
    # Critères pour identifier un titre
    if len(line) < 3 or len(line) > 100:
        return False
    
    # Titres numérotés
    if re.match(r'^[IVX]+[\.\)]\s+', line) or re.match(r'^[0-9]+[\.\)]\s+', line):
        return True
    
    # Titres en majuscules
    if line.isupper() and len(line.split()) <= 8:
        return True
    
    # Titres avec mots-clés
    mots_titre = ['introduction', 'conclusion', 'développement', 'partie', 'exercice', 'question']
    if any(mot in line.lower() for mot in mots_titre):
        return True
    
    return False

def est_liste(line: str) -> bool:
    """Détermine si une ligne fait partie d'une liste"""
    line = line.strip()
    
    # Listes à puces
    if re.match(r'^[-•*]\s+', line):
        return True
    
    # Listes numérotées
    if re.match(r'^[0-9]+[\.\)]\s+', line):
        return True
    
    # Listes alphabétiques
    if re.match(r'^[a-z][\.\)]\s+', line):
        return True
    
    return False

def classifier_formule(contenu: str) -> str:
    """Classifie le type d'une formule mathématique"""
    if '=' in contenu:
        if any(op in contenu for op in ['+', '-', '*', '/', '^']):
            return 'equation'
        else:
            return 'egalite'
    elif any(op in contenu for op in ['<', '>', '≤', '≥', '≠']):
        return 'inequation'
    elif '(' in contenu and ')' in contenu:
        return 'fonction'
    elif any(char.isdigit() for char in contenu):
        return 'calcul'
    else:
        return 'expression'

def detecter_type_exercice(chemin: str) -> str:
    """Détecte le type d'exercice depuis le nom de fichier"""
    nom = os.path.basename(chemin).lower()
    
    if 'dissertation' in nom or 'redaction' in nom:
        return 'dissertation'
    elif 'qcm' in nom or 'choix' in nom:
        return 'qcm'
    elif 'exercice' in nom or 'probleme' in nom:
        return 'exercice'
    elif 'question' in nom:
        return 'question_courte'
    else:
        return 'redaction'

# ============================================
# UTILITAIRES POUR BARÈME (consolidé depuis bareme_loader.py)
# ============================================

def evaluer_mots_cles(reponse: str, mots_cles: List[str], points_max: float) -> float:
    """Évalue la présence des mots-clés dans la réponse"""
    if not mots_cles:
        return points_max
    
    reponse_lower = reponse.lower()
    mots_trouves = sum(1 for mot in mots_cles if mot.lower() in reponse_lower)
    
    return (mots_trouves / len(mots_cles)) * points_max

def evaluer_concepts(reponse: str, concepts: List[str], points_max: float) -> float:
    """Évalue la présence des concepts essentiels"""
    if not concepts:
        return points_max
    
    reponse_lower = reponse.lower()
    concepts_trouves = 0
    
    for concept in concepts:
        # Recherche flexible (synonymes possibles)
        if any(mot in reponse_lower for mot in concept.lower().split()):
            concepts_trouves += 1
    
    return (concepts_trouves / len(concepts)) * points_max

def evaluer_exemples(reponse: str, exemples_ref: List[str], points_max: float) -> float:
    """Évalue la qualité des exemples donnés"""
    if not exemples_ref:
        return points_max * 0.5  # Points par défaut si pas d'exemples de référence
    
    # Détecter si la réponse contient des exemples
    marqueurs_exemples = ['exemple', 'par exemple', 'notamment', 'comme', 'tel que']
    a_des_exemples = any(marqueur in reponse.lower() for marqueur in marqueurs_exemples)
    
    if a_des_exemples:
        return points_max
    else:
        return points_max * 0.3  # Pénalité si pas d'exemples

def appliquer_penalites_erreurs(reponse: str, erreurs_freq: List[Dict]) -> float:
    """Applique les pénalités pour erreurs fréquentes"""
    penalite_totale = 0.0
    
    for erreur_info in erreurs_freq:
        erreur = erreur_info.get('erreur', '')
        penalite = float(erreur_info.get('penalite', 0))
        
        if erreur.lower() in reponse.lower():
            penalite_totale += penalite
    
    return penalite_totale

def generer_justifications(detail_points: Dict, corrige_ref) -> List[str]:
    """Génère les justifications pour l'attribution des points"""
    justifications = []
    
    for critere, points in detail_points.items():
        if critere == "mots_cles" and points > 0:
            justifications.append(f"Mots-clés présents: +{points:.1f} pts")
        elif critere == "concepts" and points > 0:
            justifications.append(f"Concepts maîtrisés: +{points:.1f} pts")
        elif critere == "penalites" and points < 0:
            justifications.append(f"Erreurs détectées: {points:.1f} pts")
    
    return justifications

def adapter_criteres_niveau(criteres: Dict, classe: str) -> Dict:
    """Adapte les critères selon le niveau de classe"""
    
    # Facteurs d'adaptation par niveau
    facteurs_niveau = {
        "6eme": {"orthographe": 1.5, "vocabulaire": 0.8, "structure": 0.9},
        "5eme": {"orthographe": 1.3, "vocabulaire": 0.9, "structure": 0.95},
        "4eme": {"orthographe": 1.1, "vocabulaire": 1.0, "structure": 1.0},
        "3eme": {"orthographe": 1.0, "vocabulaire": 1.1, "structure": 1.1},
        "seconde": {"orthographe": 0.9, "vocabulaire": 1.2, "structure": 1.2},
        "1ere": {"orthographe": 0.8, "vocabulaire": 1.3, "structure": 1.3},
        "terminale": {"orthographe": 0.7, "vocabulaire": 1.4, "structure": 1.4}
    }
    
    facteurs = facteurs_niveau.get(classe.lower(), {})
    
    for critere in criteres:
        if critere in facteurs:
            for key in criteres[critere]:
                if isinstance(criteres[critere][key], (int, float)):
                    criteres[critere][key] *= facteurs[critere]
    
    return criteres

def get_ajustements_niveau(niveau: str) -> Dict:
    """Retourne les ajustements standard par niveau"""
    
    ajustements_niveaux = {
        "6eme": {
            "facteurs_criteres": {"orthographe": 1.5, "structure": 0.8},
            "tolerance_orthographe": 1.5
        },
        "5eme": {
            "facteurs_criteres": {"orthographe": 1.3, "structure": 0.9},
            "tolerance_orthographe": 1.3
        },
        "4eme": {
            "facteurs_criteres": {"orthographe": 1.1, "structure": 1.0},
            "tolerance_orthographe": 1.1
        },
        "3eme": {
            "facteurs_criteres": {"orthographe": 1.0, "structure": 1.1},
            "tolerance_orthographe": 1.0
        },
        "seconde": {
            "facteurs_criteres": {"orthographe": 0.9, "structure": 1.2},
            "tolerance_orthographe": 0.9
        },
        "1ere": {
            "facteurs_criteres": {"orthographe": 0.8, "structure": 1.3},
            "tolerance_orthographe": 0.8
        },
        "terminale": {
            "facteurs_criteres": {"orthographe": 0.7, "structure": 1.4},
            "tolerance_orthographe": 0.7
        }
    }
    
    return ajustements_niveaux.get(niveau.lower(), {
        "facteurs_criteres": {},
        "tolerance_orthographe": 1.0
    })

# ============================================
# UTILITAIRES DE TRAITEMENT D'IMAGES (consolidé depuis charger_copies.py)
# ============================================

def maj_statistiques(stats: Dict, transcription):
    """Met à jour les statistiques globales"""
    if hasattr(transcription, 'qualite_ecriture'):
        qualite = transcription.qualite_ecriture
    else:
        qualite = getattr(transcription, 'qualite_ecriture', 'INCONNUE')
    
    if qualite == 'EXCELLENTE':
        stats['copies_excellentes'] += 1
    elif qualite == 'BONNE':
        stats['copies_bonnes'] += 1
    elif qualite == 'MOYENNE':
        stats['copies_moyennes'] += 1
    else:
        stats['copies_difficiles'] += 1
    
    if hasattr(transcription, 'mots_incertains'):
        stats['mots_incertains_total'] += len(transcription.mots_incertains)

def generer_resume_transcriptions(resultats: Dict) -> Dict:
    """Génère un résumé des transcriptions"""
    stats = resultats['statistiques']
    total = stats['total_copies']
    
    return {
        'taux_succes': f"{((stats['copies_excellentes'] + stats['copies_bonnes'])/total*100):.1f}%" if total > 0 else "0%",
        'taux_difficulte': f"{(stats['copies_difficiles']/total*100):.1f}%" if total > 0 else "0%",
        'moyenne_mots_incertains': stats['mots_incertains_total'] / total if total > 0 else 0,
        'recommandation_globale': generer_recommandation_globale(stats)
    }

def generer_recommandation_globale(stats: Dict) -> str:
    """Génère une recommandation basée sur les statistiques"""
    total = stats['total_copies']
    taux_difficulte = stats['copies_difficiles'] / total if total > 0 else 0
    
    if taux_difficulte > 0.5:
        return "Améliorer la qualité des images avant OCR"
    elif taux_difficulte > 0.3:
        return "Qualité correcte, quelques corrections manuelles nécessaires"
    else:
        return "Excellente qualité de transcription automatique"

# ============================================
# CONSTANTES ET CONFIGURATION
# ============================================

# Extensions de fichiers supportées
EXTENSIONS_IMAGES = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
EXTENSIONS_PDF = ['.pdf']
EXTENSIONS_BAREME = ['.json', '.yaml', '.yml', '.xlsx', '.xls']
EXTENSIONS_CORRIGE = ['.txt', '.md', '.json', '.docx']

# Schémas de validation courants
SCHEMA_CONFIG_AGENT = {
    'matiere': {'type': str, 'required': True, 'choices': ['francais', 'mathematiques', 'histoire', 'general']},
    'classe': {'type': str, 'required': True},
    'type_exercice': {'type': str, 'default': 'redaction'},
    'qualite_ocr_min': {'type': str, 'default': 'MOYENNE', 'choices': ['EXCELLENTE', 'BONNE', 'MOYENNE', 'FAIBLE']},
    'confiance_correction_min': {'type': float, 'default': 70.0, 'min': 0.0, 'max': 100.0}
}

# Messages d'erreur standards
MESSAGES_ERREUR = {
    'fichier_inexistant': "Le fichier spécifié n'existe pas",
    'format_non_supporte': "Format de fichier non supporté",
    'erreur_ocr': "Erreur lors de la transcription OCR",
    'erreur_correction': "Erreur lors de la correction",
    'api_indisponible': "Service API indisponible",
    'configuration_invalide': "Configuration invalide"
}

# ============================================
# EXPORTS ET ALIAS
# ============================================

# Fonctions principales exportées
__all__ = [
    # Logging
    'init_logger', 'safe_print',
    
    # Gestion texte
    'safe_text_handling', 'nettoyer_texte_ocr', 'extraire_mots_cles', 
    'detecter_langue', 'normaliser_texte_pour_comparaison', 'calculer_similarite_textuelle',
    
    # Validation
    'valider_chemin_fichier', 'valider_configuration',
    
    # OCR helpers
    'extraire_nombres_du_texte', 'encode_image_to_base64', 'extraire_mots_incertains',
    'est_titre', 'est_liste', 'classifier_formule', 'detecter_type_exercice',
    
    # Barème helpers
    'evaluer_mots_cles', 'evaluer_concepts', 'evaluer_exemples', 'appliquer_penalites_erreurs',
    'generer_justifications', 'adapter_criteres_niveau', 'get_ajustements_niveau',
    
    # Image processing helpers
    'maj_statistiques', 'generer_resume_transcriptions', 'generer_recommandation_globale',
    
    # Gestion erreurs
    'gestion_erreur_robuste', 'creer_rapport_erreur',
    
    # Formatage
    'formater_note', 'convertir_dict_en_json_safe', 'generer_nom_fichier_unique',
    
    # Constantes
    'EXTENSIONS_IMAGES', 'EXTENSIONS_PDF', 'EXTENSIONS_BAREME', 'EXTENSIONS_CORRIGE',
    'SCHEMA_CONFIG_AGENT', 'MESSAGES_ERREUR'
]

# ============================================
# INITIALISATION DU MODULE
# ============================================

# Initialiser le logger par défaut
_default_logger = init_logger()

# Message de démarrage (optionnel, en mode debug)
if os.getenv('DEBUG_CORRECTION'):
    safe_print("🛠️ Module utils_correction consolidé initialisé", "DEBUG")