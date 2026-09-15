# AI Notes Backend

Backend IA (résumé, recherche sémantique, chat) pour une application de notes, construit avec
**FastAPI** et **SQLite**. Expose une API REST consommée par une app iOS (voir le dépôt
compagnon [`ai-notes-ios`](https://github.com/WajihBenabdessalem/ai-notes-ios)), mais reste
totalement indépendant — testable et utilisable seul, depuis n'importe quel client HTTP.

Projet réalisé par [Wajih Benabdessalem](https://www.linkedin.com/in/wajihabdessalem)
dans le cadre d'une transition de Senior Software Engineer (iOS) vers l'AI Engineering.

## Fonctionnalités

- **CRUD de notes** (création, liste, détail, suppression) persistées en SQLite
- **Résumé IA** d'une note (`POST /notes/{id}/summarize`)
- **Recherche sémantique** sur l'ensemble des notes, via embeddings + similarité cosinus
  implémentée à la main (`POST /search`) — pas de dépendance à une base vectorielle externe
- **Chat RAG-lite** : répond aux questions de l'utilisateur en s'appuyant sur ses notes les
  plus pertinentes (`POST /chat`)
- **Fonctionne hors ligne / sans clé API** : chaque appel IA a un repli déterministe (embedding
  par hash, réponse simulée), ce qui permet de développer et tester tout le pipeline sans
  dépendance réseau ni coût — voir la section [Mode hors ligne](#mode-hors-ligne-sans-clé-api).

## Stack technique

- **Langage** : Python 3.11+
- **API** : FastAPI + Uvicorn
- **Persistance** : SQLite via SQLModel
- **LLM & embeddings** : SDK OpenAI natif (pas de framework d'orchestration — volontairement,
  pour un besoin simple qui ne justifie pas une dépendance supplémentaire)
- **Tests** : Pytest, base en mémoire, aucun appel réseau requis
- **Qualité** : Ruff (lint), GitHub Actions (CI)
- **Déploiement** : Docker / docker-compose

## Structure

```
src/notes_backend/
├── config.py                   # Configuration (pydantic-settings)
├── db.py                       # Connexion SQLite (fichier ou mémoire selon l'environnement)
├── models.py                   # Modèle de persistance Note (embedding stocké en JSON)
├── embeddings.py               # Calcul d'embeddings + repli déterministe hors ligne
├── llm.py                      # Génération de texte + repli déterministe hors ligne
├── similarity.py               # Similarité cosinus "maison" (pas de FAISS/Chroma)
├── services/
│   ├── notes_service.py        # CRUD
│   ├── summarize_service.py    # Résumé d'une note
│   ├── search_service.py       # Recherche sémantique
│   └── chat_service.py         # Chat RAG-lite
└── api/
    ├── main.py                 # Endpoints FastAPI
    └── schemas.py               # Schémas Pydantic

tests/                          # 28 tests, aucune dépendance réseau
docker/                         # Dockerfile + docker-compose
```

## Installation

```bash
git clone https://github.com/WajihBenabdessalem/ai-notes-backend.git
cd ai-notes-backend

python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate

make install                   # ou : pip install -r requirements-dev.txt

cp .env.example .env
# Renseigner OPENAI_API_KEY dans .env (optionnel — voir Mode hors ligne)
```

## Utilisation

```bash
make run
# Documentation interactive : http://localhost:8000/docs
```

```bash
# Créer une note
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Congés", "content": "25 jours de congés payés par an"}'

# Chercher dans ses notes
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "combien de jours de congés"}'

# Discuter avec ses notes
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Combien de jours de congés ai-je par an ?"}'
```

### Avec Docker

```bash
cd docker
docker compose up --build
```

## Tests

```bash
make test
```

28 tests, exécutés entièrement hors ligne (voir section suivante) : CRUD, calcul de similarité,
services (résumé/recherche/chat), et l'API bout en bout avec une base SQLite en mémoire par test.

## Mode hors ligne (sans clé API)

Si `OPENAI_API_KEY` n'est pas renseignée, `embeddings.py` et `llm.py` basculent automatiquement
sur un repli déterministe :

- **Embedding** : un hash SHA-256 normalisé du texte — **aucune sémantique réelle**, sert
  uniquement à garder la mécanique (indexation, classement par similarité) fonctionnelle et
  testable sans réseau.
- **Génération** : une chaîne fixe indiquant qu'aucune clé API n'est configurée.

Ce mode permet de développer, tester et faire une démo du pipeline complet sans dépendance
externe ni coût. **Avec une vraie clé OpenAI, exactement le même code produit de vrais
résumés et une vraie recherche sémantique** — aucune autre modification nécessaire.

## Choix de conception

- **Recherche vectorielle "maison"** (cosinus, ~15 lignes) plutôt qu'une base vectorielle
  dédiée : suffisant jusqu'à quelques milliers de notes par utilisateur, et démontre la
  mécanique sous-jacente plutôt que de s'appuyer sur une boîte noire. Au-delà, un vrai index
  (FAISS, pgvector) serait nécessaire.
- **SDK OpenAI natif** plutôt que LangChain : pour un besoin aussi direct (un appel
  d'embedding, un appel de chat), une couche d'orchestration n'apporte rien.
- **Repli déterministe systématique** : chaque fonction qui appelle une API externe a un
  chemin de secours testable, ce qui rend la CI rapide, gratuite et fiable.

## Limites connues

- Pas d'authentification : toutes les notes sont actuellement dans une base partagée, sans
  notion d'utilisateur. À ajouter avant tout usage réel multi-utilisateur.
- Recherche en O(n) sur l'ensemble des notes à chaque requête — ne scale pas au-delà de
  quelques milliers de notes.
- Pas d'évaluation automatisée de la qualité des réponses générées (type RAGAS) — les tests
  valident le pipeline, pas la pertinence sémantique des réponses.

## Licence

MIT — voir [LICENSE](LICENSE).
