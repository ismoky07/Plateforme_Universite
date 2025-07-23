import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageEnhance
import fitz  # PyMuPDF

# Import des modèles consolidés
from models_correction import StructureCopie

# Import des utilitaires consolidés
from utils_correction import safe_print

def charger_copies_examen(dossier_path: str, formats_acceptes: List[str] = None) -> Dict[str, List[str]]:
    """Charge tous les fichiers de copies d'examen d'un dossier"""
    if formats_acceptes is None:
        formats_acceptes = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    
    dossier_path = dossier_path.replace('\\', '/')
    safe_print(f"📁 Chargement copies: {dossier_path}")
    
    resultats = {'images': [], 'pdfs': [], 'rejetes': [], 'statistiques': {'total_fichiers': 0, 'fichiers_valides': 0, 'fichiers_rejetes': 0}}
    
    try:
        if not os.path.exists(dossier_path):
            safe_print(f"❌ Dossier inexistant: {dossier_path}")
            return resultats
        
        for fichier in os.listdir(dossier_path):
            chemin_complet = f"{dossier_path}/{fichier}"
            resultats['statistiques']['total_fichiers'] += 1
            
            extension = Path(fichier).suffix.lower()
            if extension not in formats_acceptes:
                resultats['rejetes'].append({'chemin': chemin_complet, 'raison': f"Format non supporté: {extension}"})
                resultats['statistiques']['fichiers_rejetes'] += 1
                continue
            
            try:
                taille_fichier = os.path.getsize(chemin_complet)
                if taille_fichier == 0:
                    resultats['rejetes'].append({'chemin': chemin_complet, 'raison': "Fichier vide"})
                    resultats['statistiques']['fichiers_rejetes'] += 1
                    continue
                
                if extension == '.pdf':
                    resultats['pdfs'].append(chemin_complet)
                else:
                    resultats['images'].append(chemin_complet)
                
                resultats['statistiques']['fichiers_valides'] += 1
                safe_print(f"✅ {fichier}")
                
            except Exception as e:
                resultats['rejetes'].append({'chemin': chemin_complet, 'raison': f"Erreur: {str(e)}"})
                resultats['statistiques']['fichiers_rejetes'] += 1
        
        safe_print(f"📊 Total: {resultats['statistiques']['total_fichiers']}, Valides: {resultats['statistiques']['fichiers_valides']}")
        
    except Exception as e:
        safe_print(f"❌ Erreur chargement: {str(e)}")
        resultats['erreur_globale'] = str(e)
    
    return resultats

def detecter_structure_copie(chemin_image: str, config_detection: Dict = None) -> StructureCopie:
    """Détecte la structure d'une copie d'examen"""
    if config_detection is None:
        config_detection = {'detecter_questions': True, 'analyser_qualite': True, 'taille_min_zone': 1000}
    
    safe_print(f"🔍 Analyse: {os.path.basename(chemin_image)}")
    
    structure = StructureCopie(
        nom_fichier=os.path.basename(chemin_image), nombre_pages=1, pages_detectees=[chemin_image],
        zones_questions=[], qualite_images=[], orientation_correcte=True, format_valide=True, erreurs_detectees=[]
    )
    
    try:
        image = cv2.imread(chemin_image)
        if image is None:
            structure.format_valide = False
            structure.erreurs_detectees.append("Image non lisible")
            return structure
        
        height, width = image.shape[:2]
        
        # Analyser qualité
        if config_detection['analyser_qualite']:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            contraste = np.std(gray)
            nettete = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if contraste > 60 and nettete > 100:
                qualite = "EXCELLENTE"
            elif contraste > 45 and nettete > 50:
                qualite = "BONNE"
            elif contraste > 30 and nettete > 20:
                qualite = "MOYENNE"
            else:
                qualite = "FAIBLE"
            
            structure.qualite_images.append(qualite)
            safe_print(f"   Qualité: {qualite}")
        
        # Détecter zones questions
        if config_detection['detecter_questions']:
            zones = _detecter_zones_questions(image, config_detection)
            structure.zones_questions = zones
            safe_print(f"   Zones: {len(zones)}")
        
        # Vérifications lisibilité
        luminosite = np.mean(gray)
        if luminosite < 50:
            structure.erreurs_detectees.append("Image trop sombre")
        elif luminosite > 200:
            structure.erreurs_detectees.append("Image surexposée")
        
        if nettete < 20:
            structure.erreurs_detectees.append("Image floue")
        
        safe_print(f"✅ Analyse: {len(structure.erreurs_detectees)} erreur(s)")
        
    except Exception as e:
        safe_print(f"❌ Erreur: {str(e)}")
        structure.erreurs_detectees.append(f"Erreur: {str(e)}")
        structure.format_valide = False
    
    return structure

def preprocesser_image(chemin_image: str, output_dir: str = None, options: Dict = None) -> str:
    """Améliore la qualité d'une image pour l'OCR"""
    if options is None:
        options = {'ameliorer_contraste': True, 'reduire_bruit': True, 'augmenter_nettete': True, 'largeur_max': 2000}
    
    safe_print(f"🔧 Preprocessing: {os.path.basename(chemin_image)}")
    
    try:
        # Chemin sortie
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            nom_fichier = Path(chemin_image).stem + "_preprocessed.png"
            chemin_sortie = os.path.join(output_dir, nom_fichier)
        else:
            chemin_sortie = chemin_image.replace('.', '_preprocessed.')
        
        # Charger et traiter
        image_pil = Image.open(chemin_image)
        if image_pil.mode != 'RGB':
            image_pil = image_pil.convert('RGB')
        
        # Redimensionner si nécessaire
        if image_pil.width > options['largeur_max']:
            ratio = options['largeur_max'] / image_pil.width
            nouvelle_hauteur = int(image_pil.height * ratio)
            image_pil = image_pil.resize((options['largeur_max'], nouvelle_hauteur), Image.Resampling.LANCZOS)
        
        # Améliorations
        if options['ameliorer_contraste']:
            image_pil = ImageEnhance.Contrast(image_pil).enhance(1.2)
        if options['augmenter_nettete']:
            image_pil = ImageEnhance.Sharpness(image_pil).enhance(1.1)
        
        # Débruitage avec OpenCV
        if options['reduire_bruit']:
            image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            image_cv = cv2.fastNlMeansDenoisingColored(image_cv, None, 10, 10, 7, 21)
            image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
        
        # Sauvegarder
        image_pil.save(chemin_sortie, 'PNG', quality=95, optimize=True)
        safe_print(f"✅ Sauvegardé: {os.path.basename(chemin_sortie)}")
        
        return chemin_sortie
        
    except Exception as e:
        safe_print(f"❌ Erreur preprocessing: {str(e)}")
        return chemin_image

def segmenter_par_question(chemin_image: str, zones_questions: List[Dict], output_dir: str) -> List[str]:
    """Découpe une copie en segments par question"""
    safe_print(f"✂️ Segmentation: {os.path.basename(chemin_image)}")
    
    if not zones_questions:
        safe_print("   ⚠️ Aucune zone détectée")
        return [chemin_image]
    
    segments_paths = []
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        image = cv2.imread(chemin_image)
        if image is None:
            return [chemin_image]
        
        nom_base = Path(chemin_image).stem
        height, width = image.shape[:2]
        
        for i, zone in enumerate(zones_questions, 1):
            try:
                x, y, w, h = zone['bbox']
                
                # Valider coordonnées
                x = max(0, min(x, width))
                y = max(0, min(y, height))
                w = min(w, width - x)
                h = min(h, height - y)
                
                if w <= 0 or h <= 0:
                    continue
                
                # Extraire avec marge
                marge = 10
                y1 = max(0, y - marge)
                y2 = min(height, y + h + marge)
                x1 = max(0, x - marge)
                x2 = min(width, x + w + marge)
                
                segment = image[y1:y2, x1:x2]
                
                nom_segment = f"{nom_base}_question_{i:02d}.png"
                chemin_segment = os.path.join(output_dir, nom_segment)
                
                if cv2.imwrite(chemin_segment, segment):
                    segments_paths.append(chemin_segment)
                    safe_print(f"   ✅ Q{i}: {nom_segment}")
                
            except Exception as e:
                safe_print(f"   ❌ Erreur Q{i}: {str(e)}")
                continue
        
        safe_print(f"✅ {len(segments_paths)} segments créés")
        return segments_paths if segments_paths else [chemin_image]
        
    except Exception as e:
        safe_print(f"❌ Erreur segmentation: {str(e)}")
        return [chemin_image]

def valider_format_copie(chemin_fichier: str, criteres: Dict = None) -> Dict[str, any]:
    """Vérifie qu'une copie est exploitable"""
    if criteres is None:
        criteres = {'resolution_min': (800, 600), 'taille_max': 20*1024*1024, 'contraste_min': 30}
    
    safe_print(f"🔍 Validation: {os.path.basename(chemin_fichier)}")
    
    validation = {'valide': True, 'erreurs': [], 'avertissements': [], 'scores': {}, 'recommandations': []}
    
    try:
        if not os.path.exists(chemin_fichier):
            validation['valide'] = False
            validation['erreurs'].append("Fichier inexistant")
            return validation
        
        extension = Path(chemin_fichier).suffix.lower()
        taille = os.path.getsize(chemin_fichier)
        
        if taille > criteres['taille_max']:
            validation['avertissements'].append(f"Fichier volumineux: {taille/1024/1024:.1f}MB")
        
        if extension == '.pdf':
            try:
                doc = fitz.open(chemin_fichier)
                nb_pages = len(doc)
                validation['scores']['pdf_pages'] = nb_pages
                doc.close()
                
                if nb_pages == 0:
                    validation['valide'] = False
                    validation['erreurs'].append("PDF vide")
            except Exception as e:
                validation['valide'] = False
                validation['erreurs'].append(f"Erreur PDF: {str(e)}")
        
        else:  # Image
            image = cv2.imread(chemin_fichier)
            if image is None:
                validation['valide'] = False
                validation['erreurs'].append("Image non lisible")
                return validation
            
            height, width = image.shape[:2]
            validation['scores']['resolution'] = (width, height)
            
            if width < criteres['resolution_min'][0] or height < criteres['resolution_min'][1]:
                validation['erreurs'].append(f"Résolution faible: {width}x{height}")
                validation['valide'] = False
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            contraste = np.std(gray)
            nettete = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            validation['scores']['contraste'] = contraste
            validation['scores']['nettete'] = nettete
            
            if contraste < criteres['contraste_min']:
                validation['avertissements'].append(f"Contraste faible: {contraste:.1f}")
            if nettete < 50:
                validation['avertissements'].append(f"Image floue: {nettete:.1f}")
        
        # Recommandations
        if validation['erreurs']:
            validation['recommandations'].append("Vérifier qualité du scan")
        if any("contraste" in av for av in validation['avertissements']):
            validation['recommandations'].append("Améliorer éclairage")
        if any("floue" in av for av in validation['avertissements']):
            validation['recommandations'].append("Stabiliser appareil photo")
        
        status = "✅ Valide" if validation['valide'] else "❌ Invalide"
        safe_print(f"   {status} ({len(validation['avertissements'])} avert.)")
    
    except Exception as e:
        safe_print(f"❌ Erreur validation: {str(e)}")
        validation['valide'] = False
        validation['erreurs'].append(f"Erreur: {str(e)}")
    
    return validation

def convertir_pdf_en_images_copies(pdf_paths: List[str], output_dir: str = None, dpi: int = 300) -> List[str]:
    """Convertit PDFs de copies en images optimisées"""
    safe_print(f"📄➡️🖼️ Conversion {len(pdf_paths)} PDF(s)")
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    images_paths = []
    
    for pdf_path in pdf_paths:
        try:
            if not os.path.exists(pdf_path):
                continue
            
            doc = fitz.open(pdf_path)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                if output_dir:
                    if len(doc) == 1:
                        image_path = os.path.join(output_dir, f"{base_name}.png")
                    else:
                        image_path = os.path.join(output_dir, f"{base_name}_page_{page_num+1:02d}.png")
                else:
                    image_path = f"{base_name}_page_{page_num+1:02d}.png"
                
                pix.save(image_path)
                images_paths.append(image_path)
                safe_print(f"   ✅ Page {page_num+1}")
                pix = None
            
            doc.close()
            
        except Exception as e:
            safe_print(f"   ❌ Erreur: {str(e)}")
            continue
    
    safe_print(f"✅ {len(images_paths)} image(s) générée(s)")
    return images_paths

def _detecter_zones_questions(image: np.ndarray, config: Dict) -> List[Dict]:
    """Détecte zones de questions dans une copie"""
    zones = []
    
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            if w * h < config.get('taille_min_zone', 1000):
                continue
            
            ratio = w / h
            if ratio < 0.1 or ratio > 10:
                continue
            
            zones.append({
                'id': i + 1,
                'bbox': (x, y, w, h),
                'aire': w * h,
                'ratio': ratio,
                'type': 'zone_texte'
            })
        
        zones.sort(key=lambda z: z['bbox'][1])  # Tri vertical
        return zones[:10] if len(zones) > 10 else zones  # Limite à 10 zones
    
    except Exception:
        return []