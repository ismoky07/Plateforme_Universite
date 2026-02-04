# Plateforme Universite

Plateforme universitaire moderne avec correction automatisee par IA.

## Architecture

```
Plateforme_Universite/
├── backend/          # FastAPI Backend (Python)
│   ├── app/
│   │   ├── api/      # Routes API REST
│   │   ├── models/   # Modeles Pydantic
│   │   ├── services/ # Logique metier
│   │   └── core/     # Utilitaires (auth, security)
│   └── data/         # Stockage donnees
│
├── frontend/         # React Frontend (TypeScript)
│   ├── src/
│   │   ├── api/      # Appels API
│   │   ├── components/ # Composants React
│   │   ├── pages/    # Pages de l'application
│   │   ├── store/    # State management (Zustand)
│   │   └── types/    # Types TypeScript
│   └── public/
│
└── docker-compose.yml
```

## Fonctionnalites

### Etudiants
- Connexion simplifiee (numero etudiant + nom)
- Consultation des examens disponibles
- Soumission de copies (scan, photo, numerique)
- Consultation des resultats et rapports

### Professeurs
- Creation et gestion d'evaluations
- Gestion des copies soumises
- Correction automatisee par IA (GPT-4)
- Publication des resultats

### Administration
- Gestion des candidatures
- Verification OCR des bulletins
- Validation/rejet des candidatures

## Demarrage rapide

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editez .env avec votre cle OpenAI
uvicorn app.main:app --reload
```

API disponible sur http://localhost:8000
Documentation: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Application disponible sur http://localhost:5173

### Docker

```bash
docker-compose up -d
```

## Comptes de demonstration

### Professeur/Admin
- Username: `admin`
- Password: `admin123`

### Professeur
- Username: `prof`
- Password: `prof123`

### Etudiant
- Numero: `12345`
- Nom: `Dupont`
- Prenom: `Jean`

## Technologies

### Backend
- **FastAPI** - Framework API REST
- **Pydantic** - Validation des donnees
- **JWT** - Authentification
- **OpenAI GPT-4** - Correction IA

### Frontend
- **React 18** - Framework UI
- **TypeScript** - Typage statique
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Navigation

## API Endpoints

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/auth/login` | Connexion |
| POST | `/api/v1/auth/login/student` | Connexion etudiant |
| GET | `/api/v1/evaluations` | Liste evaluations |
| POST | `/api/v1/evaluations` | Creer evaluation |
| POST | `/api/v1/submissions` | Soumettre copie |
| POST | `/api/v1/corrections/process` | Lancer correction IA |
| GET | `/api/v1/corrections/{id}/results` | Resultats correction |
| POST | `/api/v1/candidatures` | Deposer candidature |
| POST | `/api/v1/candidatures/{id}/validate` | Valider candidature |

## Migration depuis Streamlit

Les fichiers originaux Streamlit sont conserves dans:
- `app.py` - Application principale
- `forms/` - Module candidatures
- `admin/` - Module administration
- `agentCorrection/` - Module correction IA

La logique metier de ces fichiers peut etre migree vers `backend/app/services/`.

## Licence

Projet educatif - Universite
