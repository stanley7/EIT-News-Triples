# SOCIOTYPER

**Extract organizational relationship triplets from text using AI**

SOCIOTYPER analyzes how organizations describe their roles and relationships in institutional texts. It identifies patterns like "EIT Health **supports** startups" or "The organization **connects** entrepreneurs with investors" and structures them as triplets.

![Actor List Viewer](Images/Gradio1.png)

---

## What This Project Does

### The Problem
Researchers studying institutional dynamics need to understand organizational relationships at scale. Manually reading thousands of documents is time-consuming and inconsistent.

### The Solution
SOCIOTYPER automatically:
1. **Extracts** relationship triplets (Role → Practice → Counterrole)
2. **Validates** results against a known actor catalog
3. **Visualizes** networks of organizational relationships
4. **Exports** structured data for analysis

### Example
From: *"EIT Health supports startups in developing innovative healthcare solutions"*

| Role | Practice | Counterrole |
|------|----------|-------------|
| EIT Health | support | startups |

---

## Project Structure

```
SOCIOTYPER/
├── sociotyper/              # Python package
│   ├── core/                # Extraction, chunking, normalization
│   ├── validation/          # Triplet validation, fuzzy matching
│   ├── actors/              # Actor catalog (168 EIT organizations)
│   ├── api/                 # Flask REST API
│   └── utils/               # Config, prompts
│
├── ui/                      # Unified web interface
│   ├── index.html
│   └── static/
│
├── notebooks/               # Jupyter notebooks
│   ├── sociotyper_colab.ipynb  # Main Colab notebook
│   └── legacy/              # Original notebooks (archived)
│
├── data/                    # Data files
│   ├── datasets/            # Raw news articles (2008-2025)
│   ├── triples/             # Extracted JSON triplets
│   └── evaluation/          # Model comparison data
│
├── Papers/                  # Academic references
├── Images/                  # Screenshots
│
├── pyproject.toml           # Package configuration
├── requirements.txt         # Dependencies
├── SETUP_GUIDE.md           # Installation guide
└── README.md
```

---

## Quick Start

### Option 1: Google Colab (Easiest)

1. Open [notebooks/sociotyper_colab.ipynb](notebooks/sociotyper_colab.ipynb) in Colab
2. Run all cells to start the API server
3. Copy the ngrok URL displayed
4. Open `ui/index.html` locally and paste the URL

### Option 2: Local Installation

```bash
# Clone repository
git clone https://github.com/stanley7/EIT-News-Triples.git
cd EIT-News-Triples

# Install package
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm

# Use the package
python -c "from sociotyper import TripleExtractor; print('Ready!')"
```

### Option 3: Try the Demo

Open `mock_ui/sociotyper-demo.html` in your browser - no installation needed.

---

## Using the Web Interface

1. **Upload** - Add text files or scrape from URLs
2. **Configure** - Select AI model (Mistral, Gemma, SpaCy-LLM)
3. **Extract** - Run triplet extraction
4. **Validate** - Review and correct results
5. **Network** - Visualize relationships
6. **Results** - Export JSON/CSV data

---

## Using the Python Package

```python
from sociotyper import TripleExtractor, TripletValidator
from sociotyper.actors import get_all_actors

# Load actors (168 EIT organizations)
actors = get_all_actors()
print(f"Loaded {len(actors)} actors")

# Validate a triplet
from sociotyper import validate_triplet
triplet = {
    "role": "EIT Health",
    "practice": "support",
    "counterrole": "startups",
    "context": "EIT Health supports startups..."
}
result, reason = validate_triplet(triplet)
print(f"Valid: {result is not None}, Reason: {reason}")
```

---

## Key Concepts

### Triplet
A structured relationship: **[Role]** → **[Practice]** → **[Counterrole]**

Example: **EIT Food** → **trains** → **farmers**

### Canonical Verbs
53 institutional action verbs used for normalization:
- Funding: fund, finance, invest, grant, sponsor
- Partnership: partner, collaborate, work with, ally
- Creation: create, launch, develop, establish
- Support: support, enable, accelerate, mentor

### Actor Catalog
168 known EIT ecosystem organizations including:
- EIT Organizations (EIT Health, EIT Food, EIT Digital, etc.)
- Universities (KU Leuven, Imperial College, etc.)
- Companies (Siemens, Roche, IBM, etc.)
- Startups, Government bodies, Networks

---

## API Endpoints

When running the Flask server:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/models` | GET | List available models |
| `/extract_triplets` | POST | Extract triplets from text |
| `/scrape_url` | POST | Scrape text from URL |
| `/health` | GET | Health check |

---

## Datasets

| Dataset | Description | Count |
|---------|-------------|-------|
| Raw Articles | EIT news (2008-2025) | 171 files |
| Mistral Triples | Extracted by Mistral-7B | 386 triplets |
| Gemma Triples | Extracted by Gemma-7B | 295 triplets |

---

## Academic Background

- **Jancsary et al. (2017)** - Structural model of institutional pluralism
- **Haans & Mertens (2024)** - Web scraping for organizational research
- **Grimmer et al. (2021)** - Machine learning for social science

Full papers in `Papers/` folder.

---

## Contributing

Areas for contribution:
- Improve extraction accuracy
- Add new data sources
- Enhance the UI
- Write documentation

---

## License

Research and educational use.

---

## Contact

Open an issue on GitHub for questions or collaboration.
