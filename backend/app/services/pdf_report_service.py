"""
services/pdf_report_service.py
==============================
Generateur de rapports PDF personnalises pour les etudiants
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import io
from typing import Dict, List


class StudentReportGenerator:
    """Generateur de rapports PDF personnalises pour etudiants"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configure les styles personnalises"""

        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='AIComment',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor('#2D5016'),
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            fontName='Helvetica-Oblique'
        ))

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

        self.styles.add(ParagraphStyle(
            name='Performance',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#FF6F00'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

    def generate_student_report(
        self,
        eval_result: Dict,
        eval_info: Dict,
        student_info: Dict
    ) -> bytes:
        """
        Genere un rapport PDF complet pour un etudiant

        Args:
            eval_result: Resultats de correction
            eval_info: Informations de l'evaluation
            student_info: Informations de l'etudiant

        Returns:
            bytes: Contenu du PDF genere
        """
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Page de garde
        story.extend(self._create_cover_page(eval_result, eval_info, student_info))
        story.append(PageBreak())

        # Resume executif
        story.extend(self._create_executive_summary(eval_result, eval_info))
        story.append(Spacer(1, 20))

        # Analyse detaillee par question
        story.extend(self._create_detailed_analysis(eval_result, eval_info))
        story.append(PageBreak())

        # Performance par question
        story.extend(self._create_performance_section(eval_result))
        story.append(Spacer(1, 20))

        # Plan de revision
        story.extend(self._create_revision_plan(eval_result, eval_info))
        story.append(PageBreak())

        # Conseils personnalises
        story.extend(self._create_personalized_advice(eval_result, eval_info))

        doc.build(story)

        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data

    def _create_cover_page(
        self,
        eval_result: Dict,
        eval_info: Dict,
        student_info: Dict
    ) -> List:
        """Cree la page de garde"""
        elements = []

        elements.append(Paragraph("RAPPORT DE CORRECTION PERSONNALISE", self.styles['CustomTitle']))
        elements.append(Spacer(1, 30))

        # Informations etudiant
        student_data = [
            ['Etudiant', f"{student_info.get('prenom', '')} {student_info.get('nom', '')}"],
            ['Classe', eval_info.get('classe', 'Non specifiee')],
            ['Matiere', eval_info.get('matiere', '')],
            ['Evaluation', eval_info.get('titre', '')],
            ['Date', eval_info.get('date', datetime.now().strftime('%d/%m/%Y'))],
            ['Professeur', eval_info.get('enseignant', 'Non specifie')]
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

        # Resultats principaux
        note_totale = eval_result.get('note_totale', 0)
        note_max = eval_result.get('note_maximale', 20)
        pourcentage = eval_result.get('pourcentage', 0)

        # Couleur selon performance
        if pourcentage >= 80:
            perf_color = colors.HexColor('#4CAF50')
            perf_text = "EXCELLENT"
        elif pourcentage >= 70:
            perf_color = colors.HexColor('#2196F3')
            perf_text = "TRES BIEN"
        elif pourcentage >= 60:
            perf_color = colors.HexColor('#FF9800')
            perf_text = "BIEN"
        elif pourcentage >= 40:
            perf_color = colors.HexColor('#FF5722')
            perf_text = "MOYEN"
        else:
            perf_color = colors.HexColor('#F44336')
            perf_text = "A AMELIORER"

        results_data = [
            ['NOTE FINALE', f"{note_totale}/{note_max}"],
            ['POURCENTAGE', f"{pourcentage:.1f}%"],
            ['PERFORMANCE', perf_text],
            ['RANG CLASSE', str(eval_result.get('rang_classe', 'N/A'))]
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
            elements.append(Paragraph("DIAGNOSTIC IA", self.styles['Subtitle']))
            elements.append(Paragraph(eval_result['diagnostic_performance'], self.styles['AIComment']))

        elements.append(Spacer(1, 40))
        elements.append(Paragraph(
            f"Rapport genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
            self.styles['Normal']
        ))

        return elements

    def _create_executive_summary(self, eval_result: Dict, eval_info: Dict) -> List:
        """Cree le resume executif"""
        elements = []

        elements.append(Paragraph("RESUME EXECUTIF", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))

        # Commentaire general
        if eval_result.get('commentaires_generaux'):
            elements.append(Paragraph("Commentaire General", self.styles['Subtitle']))
            elements.append(Paragraph(eval_result['commentaires_generaux'], self.styles['Normal']))
            elements.append(Spacer(1, 15))

        # Points forts et ameliorations
        points_forts = eval_result.get('points_forts', [])
        points_amelioration = eval_result.get('points_amelioration', [])

        if points_forts or points_amelioration:
            points_data = [['POINTS FORTS', 'POINTS A AMELIORER']]

            max_len = max(len(points_forts), len(points_amelioration))
            for i in range(max_len):
                fort = f"* {points_forts[i]}" if i < len(points_forts) else ""
                amelioration = f"* {points_amelioration[i]}" if i < len(points_amelioration) else ""
                points_data.append([fort, amelioration])

            points_table = Table(points_data, colWidths=[8*cm, 8*cm])
            points_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#E8F5E8')),
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

        # Conseils personnalises
        conseils = eval_result.get('conseils_personnalises', [])
        if conseils:
            elements.append(Paragraph("Conseils Personnalises", self.styles['Subtitle']))
            for conseil in conseils:
                elements.append(Paragraph(f"* {conseil}", self.styles['Conseil']))
            elements.append(Spacer(1, 15))

        return elements

    def _create_detailed_analysis(self, eval_result: Dict, eval_info: Dict) -> List:
        """Cree l'analyse detaillee par question"""
        elements = []

        elements.append(Paragraph("ANALYSE DETAILLEE PAR QUESTION", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))

        questions = eval_result.get('questions', [])

        if not questions:
            elements.append(Paragraph("Aucune donnee detaillee disponible.", self.styles['Normal']))
            return elements

        for i, question in enumerate(questions):
            if i > 0:
                elements.append(Spacer(1, 20))

            numero = question.get('numero', i+1)
            intitule = question.get('intitule', 'Question sans titre')
            note = question.get('note', 0)
            note_max = question.get('note_max', 5)
            pourcentage = question.get('pourcentage_reussite', 0)

            if pourcentage == 0 and note_max > 0:
                pourcentage = (note / note_max) * 100

            elements.append(Paragraph(
                f"Question {numero} - {question.get('type', 'Ouverte').title()}",
                self.styles['Subtitle']
            ))

            question_details = [
                ['Enonce', intitule[:60] + '...' if len(intitule) > 60 else intitule],
                ['Note obtenue', f"{note}/{note_max} points"],
                ['Pourcentage', f"{pourcentage:.1f}%"],
                ['Niveau', self._get_performance_level(pourcentage)]
            ]

            question_table = Table(question_details, colWidths=[3*cm, 12*cm])
            question_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#495057')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
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
            commentaire = question.get('commentaire_intelligent', '')
            if commentaire:
                elements.append(Paragraph("Analyse IA", self.styles['Heading3']))
                elements.append(Paragraph(commentaire, self.styles['AIComment']))
                elements.append(Spacer(1, 10))

            # Conseil personnalise
            conseil = question.get('conseil_personnalise', '')
            if conseil:
                elements.append(Paragraph("Conseil", self.styles['Heading3']))
                elements.append(Paragraph(conseil, self.styles['Conseil']))

        return elements

    def _create_performance_section(self, eval_result: Dict) -> List:
        """Cree la section performance"""
        elements = []

        elements.append(Paragraph("PERFORMANCE PAR QUESTION", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))

        questions = eval_result.get('questions', [])

        if not questions:
            elements.append(Paragraph("Aucune donnee disponible.", self.styles['Normal']))
            return elements

        # Tableau des scores
        chart_data = [['Question', 'Score (%)', 'Niveau']]
        scores = []

        for i, q in enumerate(questions):
            pourcentage = q.get('pourcentage_reussite', 0)
            if pourcentage == 0:
                note = q.get('note', 0)
                note_max = q.get('note_max', 1)
                pourcentage = (note / note_max) * 100 if note_max > 0 else 0

            scores.append(pourcentage)
            niveau = self._get_performance_level(pourcentage)
            chart_data.append([f"Q{q.get('numero', i+1)}", f"{pourcentage:.1f}%", niveau])

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
            elements.append(Paragraph(f"Score moyen: {moyenne:.1f}%", self.styles['Performance']))
            elements.append(Paragraph(f"Meilleur score: {max(scores):.1f}%", self.styles['Normal']))
            elements.append(Paragraph(f"Score a ameliorer: {min(scores):.1f}%", self.styles['Normal']))

        return elements

    def _create_revision_plan(self, eval_result: Dict, eval_info: Dict) -> List:
        """Cree le plan de revision"""
        elements = []

        elements.append(Paragraph("PLAN DE REVISION PERSONNALISE", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))

        matiere = eval_info.get('matiere', 'Matiere')
        questions = eval_result.get('questions', [])

        # Analyser les questions par niveau
        questions_urgentes = []
        questions_amelioration = []
        questions_consolidation = []

        for q in questions:
            pourcentage = q.get('pourcentage_reussite', 0)
            if pourcentage == 0:
                note = q.get('note', 0)
                note_max = q.get('note_max', 1)
                pourcentage = (note / note_max) * 100 if note_max > 0 else 0

            if pourcentage < 40:
                questions_urgentes.append(q)
            elif pourcentage < 70:
                questions_amelioration.append(q)
            elif pourcentage < 90:
                questions_consolidation.append(q)

        elements.append(Paragraph(f"Plan pour {matiere}", self.styles['Subtitle']))
        elements.append(Spacer(1, 15))

        if questions_urgentes:
            elements.append(Paragraph("PRIORITE 1 - REVISIONS URGENTES", self.styles['Heading2']))
            for q in questions_urgentes:
                conseil = q.get('conseil_personnalise', f"Revoir la question {q.get('numero')}")
                elements.append(Paragraph(f"* Q{q.get('numero')} : {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 15))

        if questions_amelioration:
            elements.append(Paragraph("PRIORITE 2 - APPROFONDISSEMENTS", self.styles['Heading2']))
            for q in questions_amelioration:
                conseil = q.get('conseil_personnalise', f"Approfondir la question {q.get('numero')}")
                elements.append(Paragraph(f"* Q{q.get('numero')} : {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 15))

        if questions_consolidation:
            elements.append(Paragraph("PRIORITE 3 - CONSOLIDATION", self.styles['Heading2']))
            for q in questions_consolidation:
                conseil = q.get('conseil_personnalise', f"Consolider la question {q.get('numero')}")
                elements.append(Paragraph(f"* Q{q.get('numero')} : {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 15))

        # Planning suggere
        elements.append(Paragraph("PLANNING SUGGERE", self.styles['Subtitle']))
        planning_data = [
            ['Periode', 'Objectif', 'Actions'],
            ['Semaine 1', 'Revisions urgentes', 'Focus sur priorite 1'],
            ['Semaine 2', 'Approfondissements', 'Travail sur priorite 2'],
            ['Semaine 3', 'Consolidation', 'Renforcement priorite 3'],
            ['Semaine 4', 'Evaluation', 'Tests et auto-evaluation']
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
        """Cree les conseils personnalises"""
        elements = []

        elements.append(Paragraph("CONSEILS PERSONNALISES", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))

        # Conseils generaux
        conseils_generaux = eval_result.get('conseils_personnalises', [])
        if conseils_generaux:
            elements.append(Paragraph("Conseils Generaux", self.styles['Subtitle']))
            for conseil in conseils_generaux:
                elements.append(Paragraph(f"* {conseil}", self.styles['Normal']))
            elements.append(Spacer(1, 20))

        # Conseils methodologiques
        elements.append(Paragraph("Conseils Methodologiques", self.styles['Subtitle']))

        matiere = eval_info.get('matiere', 'General')
        pourcentage = eval_result.get('pourcentage', 0)
        conseils_methodo = self._get_subject_advice(matiere, pourcentage)

        for conseil in conseils_methodo:
            elements.append(Paragraph(f"* {conseil}", self.styles['Normal']))

        elements.append(Spacer(1, 20))

        # Ressources recommandees
        elements.append(Paragraph("Ressources Recommandees", self.styles['Subtitle']))
        ressources = [
            "Revoir les cours et exercices corriges en classe",
            "Utiliser des ressources en ligne (Khan Academy, Coursera, etc.)",
            "Former des groupes d'etude avec vos camarades",
            "Faire des exercices supplementaires sur vos points faibles",
            "Ne pas hesiter a demander de l'aide a votre professeur"
        ]

        for ressource in ressources:
            elements.append(Paragraph(f"* {ressource}", self.styles['Normal']))

        # Message d'encouragement
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("MESSAGE D'ENCOURAGEMENT", self.styles['Subtitle']))

        if pourcentage >= 80:
            message = "Excellent travail ! Continue sur cette lancee."
        elif pourcentage >= 60:
            message = "Bon niveau general ! Avec un peu de travail, tu peux atteindre l'excellence."
        else:
            message = "Ne te decourage pas ! Avec de la motivation et du travail regulier, tu peux ameliorer tes resultats."

        elements.append(Paragraph(message, self.styles['AIComment']))

        return elements

    def _get_performance_level(self, pourcentage: float) -> str:
        """Retourne le niveau de performance"""
        if pourcentage >= 90:
            return "Excellent"
        elif pourcentage >= 75:
            return "Tres bien"
        elif pourcentage >= 60:
            return "Bien"
        elif pourcentage >= 40:
            return "Moyen"
        else:
            return "A ameliorer"

    def _get_subject_advice(self, matiere: str, pourcentage: float) -> List[str]:
        """Retourne des conseils specifiques a la matiere"""

        conseils_base = {
            "Mathematiques": [
                "Verifiez toujours vos calculs",
                "Dessinez des schemas pour visualiser les problemes",
                "Apprenez les formules par coeur",
                "Entrainez-vous regulierement"
            ],
            "Physique": [
                "Faites attention aux unites",
                "Analysez la coherence dimensionnelle",
                "Schematisez les situations",
                "Reliez theorie et phenomenes"
            ],
            "Francais": [
                "Lisez regulierement",
                "Structurez vos idees avant de rediger",
                "Relisez-vous pour corriger",
                "Developpez votre argumentation"
            ]
        }

        conseils = conseils_base.get(matiere, [
            "Organisez regulierement vos revisions",
            "Posez des questions en cas de doute",
            "Travaillez de facon reguliere",
            "Utilisez des methodes variees"
        ])

        if pourcentage < 50:
            conseils.append("Reprenez les bases avant les notions complexes")
            conseils.append("N'hesitez pas a demander un soutien pedagogique")

        return conseils


# Interface simple
def generate_student_pdf_report(
    eval_result: Dict,
    eval_info: Dict,
    student_info: Dict
) -> bytes:
    """Interface simple pour generer un rapport PDF"""
    generator = StudentReportGenerator()
    return generator.generate_student_report(eval_result, eval_info, student_info)