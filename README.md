# EIT News Triplet Extraction

This project collects and processes news articles from the European Institute of Innovation & Technology (EIT). The aim is to extract triplets that describe the relationships between organizational actors, their practices and counterroles.

## What This Application Does

1. **Extract Triplets** - AI models extract organizational relationships (role → practice → counterrole) from text
2. **Validate Triplets** - Manually review, accept, reject, or correct extracted triplets
3. **Analyze Network** - Generate interactive network visualization from CSV embeddings using similarity clustering
4. **Export Results** - Download validated triplets, network data, and annotations as JSON   

## Datasets

**Raw News Articles**  
Scraped from the official [EIT website](https://www.eit.europa.eu/news-events/news) for the years 2008–2025. Stored year-wise in plain text files.

Google Drive CSV File: https://drive.google.com/file/d/1eZOIWNxpoFrS4crx7xzmsurGFj7qa2OE/view?usp=sharing

### Required Files
1. `EIT_Backend.ipynb` - Backend code (in UI folder)
2. `EIT_constellation_analyzer_UI.html` - Frontend interface (in UI folder)
3. `gt_graph_embedded.csv` - **Download from Google Drive**
4. Datasets in `Dataset/` folder 

## Complete Setup Guide

### PART 1: Backend Setup (Google Colab)

#### Step 1.1: Get Your ngrok Token

1. Go to https://dashboard.ngrok.com/signup
2. Sign up (free account is fine)
3. After login, go to https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy your authtoken (looks like: `2abc123def456...`)
5. **Keep this token handy** - you'll need it in Step 1.3

#### Step 1.2: Open Google Colab

1. Go to https://colab.research.google.com/
2. Click `File` → `Upload notebook`
3. Upload your `EIT_Backend.ipynb` file from the `UI/` folder
4. Wait for the notebook to load

#### Step 1.3: Configure Colab Runtime & Secrets

**A. Change Runtime to GPU:**
1. Click `Runtime` → `Change runtime type`
2. Under "Hardware accelerator", select **T4 GPU** (or A100 if available)
3. Click `Save`

**B. Add ngrok Secret:**
1. Look at the **left sidebar** in Colab
2. Click the **🔑 key icon** (Secrets)
3. Click `+ Add new secret`
4. Enter:
   - **Name**: `NGROK`
   - **Value**: Paste your ngrok token from Step 1.1
   - Toggle switch: **ON** (enable notebook access)
5. Click outside to save

#### Step 1.4: Download & Upload CSV File

**A. Download from Google Drive:**
1. Go to https://drive.google.com/file/d/1eZOIWNxpoFrS4crx7xzmsurGFj7qa2OE/view?usp=sharing
2. Click the **Download** button (top right, looks like ⬇️)
3. Save `gt_graph_embedded.csv` to your computer
4. **File size**: ~31 MB

**B. Upload to Colab:**
1. In Colab, look at the **left sidebar**
2. Click the **📁 folder icon** (Files)
3. You'll see `/content/` directory
4. Click the **📤 upload icon** (upload to session storage)
5. Select `gt_graph_embedded.csv` from your downloads
6. Wait for upload progress bar to complete (~30 seconds)
7. **VERIFY**: Check that `/content/gt_graph_embedded.csv` appears in the file list

**⚠️ CRITICAL**: The CSV file MUST be at `/content/gt_graph_embedded.csv` or network visualization will fail!

#### Step 1.5: Run the Backend

1. In the Colab notebook, find the first code cell
2. Click the **▶️ play button** on the left of the cell
3. **First-time run**: Models will download (~2-3 minutes)

4. **Wait for this message**:
   ```
   ======================================================================
   ✅ BACKEND READY
   ======================================================================
   
   📋 PASTE THIS URL IN YOUR UI:
   
      https://abc123-def456.ngrok-free.app
   
   ======================================================================

5. **COPY THE URL** - This is your backend URL (e.g., `https://abc123-def456.ngrok-free.app`)
6. **Keep Colab tab open** - Closing it will stop the backend!
   

### PART 2: Frontend Setup (HTML File)

#### Step 2.1: Open the HTML File

1. Navigate to your `UI/` folder
2. Right-click on `EIT_constellation_analyzer_UI.html`
3. Select `Open with` → Your preferred **code editor**:
   - VS Code (recommended)
   - Sublime Text
   - Notepad++
   - Any text editor

#### Step 2.2: Configure Backend URL

1. In your code editor, press `Ctrl+F` (or `Cmd+F` on Mac) to open Find
2. Search for: `const BACKEND_BASE`
3. You should see a line like:
   ```javascript
   const BACKEND_BASE = 'https://old-url-here.ngrok-free.app';
   ```

4. **Replace the URL** with the one you copied from Colab (Step 1.5):
   ```javascript
   const BACKEND_BASE = 'https://abc123-def456.ngrok-free.app';
   ```
5. **Make sure**:
   - URL starts with `https://`
   - URL ends with `.ngrok-free.app` (no `/` at the end)
  
**Example of CORRECT configuration:**
```javascript
// CORRECT ✅
const BACKEND_BASE = 'https://abc123-def456.ngrok-free.app';
```

6. **Save the file** (`Ctrl+S` or `Cmd+S`)

#### Step 2.3: Open in Browser

1. Right-click on `EIT_constellation_analyzer_UI.html`
2. Select `Open with` → **Web Browser** (Chrome, Firefox, Edge, Safari)
3. The application should load!


## References

- Jancsary, D., Meyer, R. E., Höllerer, M. A., & Barberio, V. (2017). Toward a Structural Model of Organizational-Level Institutional Pluralism and Logic Interconnectedness. *Organization Science*, 28(6), 1150–1167. https://doi.org/10.1287/orsc.2017.1160

- Haans, R. F. J., & Mertens, M. J. (2024). The Internet Never Forgets: A Four-Step Scraping Tutorial, Codebase, and Database for Longitudinal Organizational Website Data. *Organizational Research Methods*, 1–29. https://doi.org/10.1177/10944281241284941

- Grimmer, J., Roberts, M. E., & Stewart, B. M. (2021). Machine Learning for Social Science: An Agnostic Approach. *Annual Review of Political Science*, 24, 395–419. https://doi.org/10.1146/annurev-polisci-053119-015921
