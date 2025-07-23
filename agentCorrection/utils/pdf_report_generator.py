"""
utils/pdf_report_generator.py
============================
Générateur de rapports PDF personnalisés pour les étudiants
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as ReportLabImage
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import io
import base64
from typing import Dict, List, Any

class StudentReportGenerator:
    """Générateur de rapports PDF personnalisés pour étudiants"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés"""
        
        # Style titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Style sous-titre
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les commentaires IA
        self.styles.add(ParagraphStyle(
            name='AIComment',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor('#2D5016'),
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            fontName='Helvetica-Oblique',
            backColor=colors.HexColor('#F0F8E8'),
            borderColor=colors.HexColor('#8BC34A'),
            borderWidth=1,
            borderPadding=10
        ))
        
        # Style pour les conseils
        self.styles.add(ParagraphStyle(
            name='Conseil',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor('#1565C0'),
            alignment=TA_LEFT,
            leftIndent=15,
            fontName='Helvetica'
        ))
        
        # Style performance
        self.styles.add(ParagraphStyle(
            name='Performance',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#FF6F00'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_student_report(self, eval_result: Dict, eval_info: Dict, student_info: Dict) -> bytes:
        """
        Génère un rapport PDF complet pour un étudiant
        
        Returns:
            bytes: Contenu du PDF généré
        """
        
        # Créer un buffer en mémoire
        buffer = io.BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Construire le contenu
        story = []
        
        # Page de garde
        story.extend(self._create_cover_page(eval_result, eval_info, student_info))
        story.append(PageBreak())
        
        # Résumé exécutif
        story.extend(self._create_executive_summary(eval_result, eval_info))
        story.append(Spacer(1, 20))
        
        # Analyse détaillée par question
        story.extend(self._create_detailed_analysis(eval_result, eval_info))
        story.append(PageBreak())
        
        # Graphiques de performance
        story.extend(self._create_performance_charts(eval_result))
        story.append(Spacer(1, 20))
        
        # Plan de révision
        story.extend(self._create_revision_plan(eval_result, eval_info))
        story.append(PageBreak())
        
        # Conseils personnalisés
        story.extend(self._create_personalized_advice(eval_result, eval_info))
        
        # Construire le PDF
        doc.build(story)
        
        # Récupérer le contenu
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _create_cover_page(self, eval_result: Dict, eval_info: Dict, student_info: Dict) -> List:
        """Crée la page de garde"""
        
        elements = []
        
        # Titre principal
        elements.append(Paragraph("📊 RAPPORT DE CORRECTION PERSONNALISÉ", self.styles['CustomTitle']))
        elements.append(Spacer(1, 30))
        
        # Informations étudiant
        student_data = [
            ['👤 Étudiant', f"{student_info['prenom']} {student_info['nom']}"],
            ['🎓 Promotion', eval_info.get('promotion', 'Non spécifiée')],
            ['📚 Matière', eval_info['matiere']],
            ['📝 Évaluation', eval_info['titre']],
            ['📅 Date', eval_info['date']],
            ['👨‍🏫 Professeur', eval_info.get('professeur', 'Non spécifié')],
            ['⏱️ Durée', eval_info.get('duree', 'Non spécifiée')]
        ]
        
        student_table = Table(student_data, colWidths=[4*cm, 8*cm])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2E86AB')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(student_table)
        elements.append(Spacer(1, 40))
        
        # Résultats principaux
        note_totale = eval_result['note_totale']
        note_max = eval_result.get('note_maximale', 20)
        pourcentage = eval_result['pourcentage']
        
        # Déterminer la couleur selon la performance
        if pourcentage >= 80:
            perf_color = colors.HexColor('#4CAF50')  # Vert
            perf_text = "🏆 EXCELLENT"
        elif pourcentage >= 70:
            perf_color = colors.HexColor('#2196F3')  # Bleu
            perf_text = "🌟 TRÈS BIEN"
        elif pourcentage >= 60:
            perf_color = colors.HexColor('#FF9800')  # Orange
            perf_text = "👍 BIEN"
        else:
            perf_color = colors.HexColor('#F44336')  # Rouge
            perf_text = "📈 À AMÉLIORER"
        
        # Cadre de résultats
        results_data = [
            ['📊 NOTE FINALE', f"{note_totale}/{note_max}"],
            ['📈 POURCENTAGE', f"{pourcentage:.1f}%"],
            ['🎯 PERFORMANCE', perf_text],
            ['📍 RANG CLASSE', str(eval_result.get('rang_classe', 'N/A'))]
        ]
        
        results_table = Table(results_data, colWidths=[6*cm, 6*cm])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), perf_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 2, colors.white),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(results_table)
        elements.append(Spacer(1, 30))
        
        # Diagnostic IA
        if eval_result.get('diagnostic_performance'):
            elements.append(Paragraph("🎯 DIAGNOSTIC IA", self.styles['Subtitle']))
            elements.append(Paragraph(
                eval_result['diagnostic_performance'], 
                self.styles['AIComment']
            ))
        
        # Date de génération
        elements.append(Spacer(1, 40))
        elements.append(Paragraph(
            f"📅 Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['Normal']
        ))
        
        return elements
    
    def _create_executive_summary(self, eval_result: Dict, eval_info: Dict) -> List:
        """Crée le résumé exécutif"""
        
        elements = []
        
        elements.append(Paragraph("📋 RÉSUMÉ EXÉCUTIF", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))
        
        # Commentaire général
        if eval_result.get('commentaires_generaux'):
            elements.append(Paragraph("💬 Commentaire Général", self.styles['Subtitle']))
            elements.append(Paragraph(eval_result['commentaires_generaux'], self.styles['Normal']))
            elements.append(Spacer(1, 15))
        
        # Points forts et améliorations en colonnes
        points_forts = eval_result.get('points_forts', [])
        points_amelioration = eval_result.get('points_amelioration', [])
        
        if points_forts or points_amelioration:
            
            # Tableau des points forts et améliorations
            points_data = [['🎯 POINTS FORTS', '📈 POINTS À AMÉLIORER']]
            
            max_len = max(len(points_forts), len(points_amelioration))
            
            for i in range(max_len):
                fort = f"• {points_forts[i]}" if i < len(points_forts) else ""
                amelioration = f"• {points_amelioration[i]}" if i < len(points_amelioration) else ""
                points_data.append([fort, amelioration])
            
            points_table = Table(points_data, colWidths=[8*cm, 8*cm])
            points_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F5E8')),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#FFF3E0')),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#F57C00')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(points_table)
            elements.append(Spacer(1, 20))
        
        # Conseils personnalisés
        conseils = eval_result.get('conseils_personnalises', [])
        if conseils:
            elements.append(Paragraph("💡 Conseils Personnalisés", self.styles['Subtitle']))
            for conseil in conseils:
                elements.append(Paragraph(f"• {conseil}", self.styles['Conseil']))
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_detailed_analysis(self, eval_result: Dict, eval_info: Dict) -> List:
        """Crée l'analyse détaillée par question"""
        
        elements = []
        
        elements.append(Paragraph("📝 ANALYSE DÉTAILLÉE PAR QUESTION", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))
        
        questions = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
        
        if not questions:
            elements.append(Paragraph("Aucune donnée détaillée disponible.", self.styles['Normal']))
            return elements
        
        for i, question in enumerate(questions):
            if i > 0:
                elements.append(Spacer(1, 20))
            
            # En-tête de question
            numero = question.get('numero', i+1)
            intitule = question.get('intitule', 'Question sans titre')
            note = question.get('note', 0)
            note_max = question.get('note_max', question.get('points_total', 5))
            pourcentage = question.get('pourcentage_reussite', 0)
            
            if pourcentage == 0 and note_max > 0:
                pourcentage = (note / note_max) * 100
            
            # Titre de la question
            elements.append(Paragraph(
                f"Question {numero} - {question.get('type', 'Ouverte').title()}", 
                self.styles['Subtitle']
            ))
            
            # Détails de la question
            question_details = [
                ['📋 Énoncé', intitule],
                ['📊 Note obtenue', f"{note}/{note_max} points"],
                ['📈 Pourcentage', f"{pourcentage:.1f}%"],
                ['🎯 Niveau', self._get_performance_level(pourcentage)]
            ]
            
            question_table = Table(question_details, colWidths=[3*cm, 12*cm])
            question_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#495057')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(question_table)
            elements.append(Spacer(1, 10))
            
            # Commentaire intelligent
            commentaire = question.get('commentaire_intelligent', question.get('commentaire', ''))
            if commentaire:
                elements.append(Paragraph("💭 Analyse IA", self.styles['Heading3']))
                elements.append(Paragraph(commentaire, self.styles['AIComment']))
                elements.append(Spacer(1, 10))
            
            # Conseil personnalisé
            conseil = question.get('conseil_personnalise', '')
            if conseil:
                elements.append(Paragraph("💡 Conseil Personnalisé", self.styles['Heading3']))
                elements.append(Paragraph(conseil, self.styles['Conseil']))
                elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_performance_charts(self, eval_result: Dict) -> List:
        """Crée les graphiques de performance"""
        
        elements = []
        
        elements.append(Paragraph("📊 GRAPHIQUES DE PERFORMANCE", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))
        
        questions = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
        
        if not questions:
            elements.append(Paragraph("Aucune donnée disponible pour les graphiques.", self.styles['Normal']))
            return elements
        
        # Données pour le graphique
        question_labels = []
        scores = []
        
        for i, q in enumerate(questions):
            question_labels.append(f"Q{q.get('numero', i+1)}")
            pourcentage = q.get('pourcentage_reussite', 0)
            if pourcentage == 0:
                note = q.get('note', 0)
                note_max = q.get('note_max', q.get('points_total', 1))
                pourcentage = (note / note_max) * 100 if note_max > 0 else 0
            scores.append(pourcentage)
        
        # Créer un graphique en barres simple avec du texte
        elements.append(Paragraph("📈 Performance par Question", self.styles['Subtitle']))
        
        # Tableau des scores
        chart_data = [['Question', 'Score (%)', 'Niveau']]
        for i, (label, score) in enumerate(zip(question_labels, scores)):
            niveau = self._get_performance_level(score)
            chart_data.append([label, f"{score:.1f}%", niveau])
        
        chart_table = Table(chart_data, colWidths=[3*cm, 4*cm, 6*cm])
        chart_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(chart_table)
        elements.append(Spacer(1, 20))
        
        # Statistiques
        if scores:
            moyenne = sum(scores) / len(scores)
            elements.append(Paragraph(f"📊 Score moyen: {moyenne:.1f}%", self.styles['Performance']))
            
            meilleure = max(scores)
            plus_faible = min(scores)
            elements.append(Paragraph(f"🏆 Meilleur score: {meilleure:.1f}%", self.styles['Normal']))
            elements.append(Paragraph(f"📈 Score à améliorer: {plus_faible:.1f}%", self.styles['Normal']))
        
        return elements
    
    def _create_revision_plan(self, eval_result: Dict, eval_info: Dict) -> List:
        """Crée le plan de révision"""
        
        elements = []
        
        elements.append(Paragraph("📋 PLAN DE RÉVISION PERSONNALISÉ", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))
        
        matiere = eval_info.get('matiere', 'Matière')
        questions = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
        
        # Analyser les questions par niveau de performance
        questions_urgentes = []
        questions_amelioration = []
        questions_consolidation = []
        
        for q in questions:
            pourcentage = q.get('pourcentage_reussite', 0)
            if pourcentage == 0:
                note = q.get('note', 0)
                note_max = q.get('note_max', q.get('points_total', 1))
                pourcentage = (note / note_max) * 100 if note_max > 0 else 0
            
            if pourcentage < 40:
                questions_urgentes.append(q)
            elif pourcentage < 70:
                questions_amelioration.append(q)
            elif pourcentage < 90:
                questions_consolidation.append(q)
        
        # Plan structuré
        elements.append(Paragraph(f"📚 Plan pour {matiere} - {eval_info['titre']}", self.styles['Subtitle']))
        elements.append(Spacer(1, 15))
        
        if questions_urgentes:
            elements.append(Paragraph("🚨 PRIORITÉ 1 - RÉVISIONS URGENTES", self.styles['Heading2']))
            for q in questions_urgentes:
                conseil = q.get('conseil_personnalise', f"Revoir les concepts de la question {q.get('numero')}")
                elements.append(Paragraph(f"• Q{q.get('numero')} : {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 15))
        
        if questions_amelioration:
            elements.append(Paragraph("📈 PRIORITÉ 2 - APPROFONDISSEMENTS", self.styles['Heading2']))
            for q in questions_amelioration:
                conseil = q.get('conseil_personnalise', f"Approfondir la question {q.get('numero')}")
                elements.append(Paragraph(f"• Q{q.get('numero')} : {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 15))
        
        if questions_consolidation:
            elements.append(Paragraph("🎯 PRIORITÉ 3 - CONSOLIDATION", self.styles['Heading2']))
            for q in questions_consolidation:
                conseil = q.get('conseil_personnalise', f"Consolider les acquis de la question {q.get('numero')}")
                elements.append(Paragraph(f"• Q{q.get('numero')} : {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 15))
        
        # Planning suggéré
        elements.append(Paragraph("📅 PLANNING SUGGÉRÉ", self.styles['Subtitle']))
        planning_data = [
            ['📅 Période', '🎯 Objectif', '📚 Actions'],
            ['Semaine 1', 'Révisions urgentes', 'Focus sur priorité 1'],
            ['Semaine 2', 'Approfondissements', 'Travail sur priorité 2'],
            ['Semaine 3', 'Consolidation', 'Renforcement priorité 3'],
            ['Semaine 4', 'Évaluation', 'Tests et auto-évaluation']
        ]
        
        planning_table = Table(planning_data, colWidths=[3*cm, 5*cm, 7*cm])
        planning_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(planning_table)
        
        return elements
    
    def _create_personalized_advice(self, eval_result: Dict, eval_info: Dict) -> List:
        """Crée les conseils personnalisés"""
        
        elements = []
        
        elements.append(Paragraph("💡 CONSEILS PERSONNALISÉS", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))
        
        # Conseils généraux
        conseils_generaux = eval_result.get('conseils_personnalises', [])
        if conseils_generaux:
            elements.append(Paragraph("🎯 Conseils Généraux", self.styles['Subtitle']))
            for conseil in conseils_generaux:
                elements.append(Paragraph(f"• {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 20))
        
        # Conseils méthodologiques
        elements.append(Paragraph("📚 Conseils Méthodologiques", self.styles['Subtitle']))
        
        matiere = eval_info.get('matiere', 'Général')
        conseils_methodo = self._get_subject_advice(matiere, eval_result['pourcentage'])
        
        for conseil in conseils_methodo:
            elements.append(Paragraph(f"• {conseil}", self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Ressources recommandées
        elements.append(Paragraph("📖 Ressources Recommandées", self.styles['Subtitle']))
        ressources = [
            "📚 Revoir les cours et exercices corrigés en classe",
            "💻 Utiliser des ressources en ligne (Khan Academy, Coursera, etc.)",
            "👥 Former des groupes d'étude avec vos camarades",
            "🎯 Faire des exercices supplémentaires sur vos points faibles",
            "🤝 Ne pas hésiter à demander de l'aide à votre professeur"
        ]
        
        for ressource in ressources:
            elements.append(Paragraph(ressource, self.styles['Normal']))
        
        # Message d'encouragement
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("🌟 MESSAGE D'ENCOURAGEMENT", self.styles['Subtitle']))
        
        pourcentage = eval_result['pourcentage']
        if pourcentage >= 80:
            message = "Excellent travail ! Continue sur cette lancée et n'hésite pas à aider tes camarades."
        elif pourcentage >= 60:
            message = "Bon niveau général ! Avec un peu de travail supplémentaire, tu peux atteindre l'excellence."
        else:
            message = "Ne te décourage pas ! Avec de la motivation et du travail régulier, tu peux considérablement améliorer tes résultats."
        
        elements.append(Paragraph(message, self.styles['AIComment']))
        
        return elements
    
    def _get_performance_level(self, pourcentage: float) -> str:
        """Retourne le niveau de performance"""
        if pourcentage >= 90:
            return "🏆 Excellent"
        elif pourcentage >= 75:
            return "🌟 Très bien"
        elif pourcentage >= 60:
            return "👍 Bien"
        elif pourcentage >= 40:
            return "🔄 Moyen"
        else:
            return "📈 À améliorer"
    
    def _get_subject_advice(self, matiere: str, pourcentage: float) -> List[str]:
        """Retourne des conseils spécifiques à la matière"""
        
        conseils_base = {
            "Mathématiques": [
                "Vérifiez toujours vos calculs en substituant vos résultats",
                "Dessinez des schémas pour mieux visualiser les problèmes",
                "Apprenez les formules par cœur et leur domaine d'application",
                "Entraînez-vous régulièrement avec des exercices variés"
            ],
            "Physique": [
                "Faites attention aux unités dans tous vos calculs",
                "Analysez la cohérence dimensionnelle de vos résultats",
                "Schématisez les situations physiques avant de calculer",
                "Reliez toujours la théorie aux phénomènes observés"
            ],
            "Chimie": [
                "Équilibrez soigneusement toutes vos équations chimiques",
                "Maîtrisez la nomenclature et les formules de base",
                "Visualisez les structures moléculaires en 3D",
                "Respectez les règles de sécurité dans vos raisonnements"
            ],
            "Français": [
                "Lisez régulièrement pour enrichir votre vocabulaire",
                "Structurez clairement vos idées avant de rédiger",
                "Relisez-vous pour corriger orthographe et grammaire",
                "Développez votre argumentation avec des exemples précis"
            ]
        }
        
        conseils = conseils_base.get(matiere, [
            "Organisez régulièrement vos révisions",
            "Posez des questions en cas de doute",
            "Travaillez de façon régulière et constante",
            "Utilisez des méthodes d'apprentissage variées"
        ])
        
        # Adapter selon le niveau
        if pourcentage < 50:
            conseils.append("Reprenez les bases avant d'aborder des notions complexes")
            conseils.append("N'hésitez pas à demander un soutien pédagogique")
        
        return conseils

# Interface pour Streamlit
def generate_student_pdf_report(eval_result: Dict, eval_info: Dict, student_info: Dict) -> bytes:
    """Interface simple pour générer un rapport PDF"""
    
    generator = StudentReportGenerator()
    return generator.generate_student_report(eval_result, eval_info, student_info)