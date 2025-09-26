# EIT News Triplet Extraction

This project collects and processes news articles from the European Institute of Innovation & Technology (EIT). The aim is to extract triplets that describe the relationships between organizational actors, their practices and counterroles.

# Features
- Scrapes [EIT News Events](https://www.eit.europa.eu/news-events/news) (2008–2025)

- Cleans and combines article texts

- Extracts role–practice–counterrole triplets using LLMs

- Builds an actor catalog with roles, founding dates and locations

- Visualizes actor catalog using [Gradio](https://www.gradio.app/)

# Datasets
- Raw News Articles; Scraped from the official [EIT website](https://www.eit.europa.eu/news-events/news) for the years 2008–2025. Stored year-wise in plain text files.

- Synthetic Dataset: Artificially generated dataset used for testing and evaluation of the triplet extraction pipeline.

# How to run

1. Clone the repository
   
    git clone https://github.com/stanley7/EIT-News-Triples.git
   
    cd EIT-News-Triples

2. Install dependencies
   
   pip install -r requirements.txt


# References 

- Jancsary, D., Meyer, R. E., Höllerer, M. A., & Barberio, V. (2017). Toward a Structural Model of Organizational-Level Institutional Pluralism and Logic Interconnectedness. Organization Science, 28(6), 1150–1167. https://doi.org/10.1287/orsc.2017.1160

- Haans, R. F. J., & Mertens, M. J. (2024). The Internet Never Forgets: A Four-Step Scraping Tutorial, Codebase, and Database for Longitudinal Organizational Website Data. Organizational Research Methods, 1–29. https://doi.org/10.1177/10944281241284941

- Grimmer, J., Roberts, M. E., & Stewart, B. M. (2021). Machine Learning for Social Science: An Agnostic Approach. Annual Review of Political Science, 24, 395–419. https://doi.org/10.1146/annurev-polisci-053119-015921





