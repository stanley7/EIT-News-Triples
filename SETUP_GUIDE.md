# SOCIOTYPER Setup Guide

A step-by-step guide for getting started, even if you've never used Python before.

---

## Choose Your Path

| Your Experience Level | Recommended Option |
|-----------------------|-------------------|
| Never used Python | **Option A**: Try the Demo |
| Some coding experience | **Option B**: Google Colab |
| Comfortable with Python | **Option C**: Local Installation |

---

## Option A: Try the Demo (No Installation)

**Time needed: 2 minutes**

This lets you explore the interface without installing anything.

1. Download or clone this repository
2. Open the `mock_ui` folder
3. Double-click on `eit-analyzer(5).html`
4. The demo opens in your web browser

**What you can do:**
- Explore all 7 tabs of the interface
- See how triplet extraction works
- View the network visualization
- Understand the workflow

**Limitations:**
- Uses sample data only
- Cannot process your own documents

---

## Option B: Google Colab (Easiest for Real Analysis)

**Time needed: 10-15 minutes**

Google Colab runs Python in your browser - no installation needed on your computer.

### Step 1: Get a Google Account

If you don't have one, create a free account at [accounts.google.com](https://accounts.google.com)

### Step 2: Open Google Colab

Go to [colab.research.google.com](https://colab.research.google.com)

### Step 3: Upload a Notebook

1. Click **File** → **Upload notebook**
2. Navigate to this project's `Code` folder
3. Select one of these notebooks:
   - `Actor_Catalog.ipynb` - Build an organization database
   - `Spacy-LLM/EIT_Triple_Extraction_Mistral7B.ipynb` - Extract triplets

### Step 4: Run the Notebook

1. Click **Runtime** → **Run all**
2. If prompted, click **Run anyway** (the code is safe)
3. Wait for each cell to complete (green checkmarks appear)

### Tips for Colab

- **Free GPU**: Click **Runtime** → **Change runtime type** → Select **T4 GPU**
- **Save your work**: Click **File** → **Save a copy in Drive**
- **Session timeout**: Colab disconnects after ~90 minutes of inactivity

---

## Option C: Local Installation (Full Control)

**Time needed: 30-60 minutes**

Install everything on your own computer for the best performance.

### Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.10 or newer
3. **Important**: Check "Add Python to PATH" during installation
4. Complete the installation

**Verify it worked:**
Open Command Prompt (Windows) or Terminal (Mac/Linux) and type:
```
python --version
```
You should see something like `Python 3.10.x`

### Step 2: Install Git

1. Go to [git-scm.com/downloads](https://git-scm.com/downloads)
2. Download and install for your operating system
3. Use all default settings

### Step 3: Download SOCIOTYPER

Open Command Prompt/Terminal and run:
```
git clone https://github.com/stanley7/EIT-News-Triples.git
cd EIT-News-Triples
```

Or download the ZIP file from GitHub and extract it.

### Step 4: Create a Virtual Environment (Recommended)

This keeps SOCIOTYPER's packages separate from other Python projects:

**Windows:**
```
python -m venv sociotyper_env
sociotyper_env\Scripts\activate
```

**Mac/Linux:**
```
python -m venv sociotyper_env
source sociotyper_env/bin/activate
```

You'll see `(sociotyper_env)` at the start of your command line when activated.

### Step 5: Install Dependencies

```
pip install -r requirements.txt
```

This may take 5-10 minutes. You'll see packages being downloaded.

### Step 6: Download the Language Model

```
python -m spacy download en_core_web_sm
```

### Step 7: Install Jupyter

```
pip install jupyter
```

### Step 8: Start Jupyter

```
jupyter notebook
```

Your web browser will open with the Jupyter interface. Navigate to the `Code` folder and open any notebook.

---

## Running the Web Interface

The full web interface requires both a backend (Python) and frontend (HTML).

### Step 1: Start the Backend

1. Open `UI/EIT_constellation_analyzer_backend.ipynb` in Jupyter or Colab
2. Run all cells
3. The last cell will display an **ngrok URL** (looks like `https://xxxx.ngrok.io`)
4. Copy this URL

### Step 2: Open the Frontend

1. Open `UI/EIT_constellation_analyzer_UI.html` in a text editor
2. Find the line with `API_BASE_URL`
3. Replace the URL with your ngrok URL from Step 1
4. Save the file
5. Open the HTML file in your browser

---

## Troubleshooting

### "Python is not recognized"

**Windows:** Python wasn't added to PATH. Reinstall Python and check "Add Python to PATH"

**Mac:** Try `python3` instead of `python`

### "pip is not recognized"

Try `python -m pip install` instead of `pip install`

### "Module not found" error

Make sure you:
1. Activated your virtual environment
2. Ran `pip install -r requirements.txt`

### Jupyter won't start

Try:
```
python -m jupyter notebook
```

### Out of memory errors

The local AI models need significant RAM:
- Mistral-7B: 16GB RAM minimum
- Use Google Colab with GPU for free access to more resources

### Colab disconnects

- Click **Reconnect** when prompted
- Consider Colab Pro for longer sessions
- Save your work frequently

---

## Getting Help

1. Check the [README](README.md) for project overview
2. Look in the `Papers` folder for research background
3. Open an issue on GitHub for bugs or questions

---

## Next Steps

Once you're set up:

1. **Explore the data**: Look in `Datasets/` to see the raw news articles
2. **View extracted triplets**: Open files in `Triples/` folder
3. **Run an extraction**: Try the notebooks in `Code/Spacy-LLM/`
4. **Validate results**: Use the web interface to review AI extractions

Happy analyzing!
