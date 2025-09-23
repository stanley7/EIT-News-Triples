# EIT News Triplet Extraction

This project collects and processes news articles from the European Institute of Innovation & Technology (EIT). The aim is to extract triplets that describe the relationships between organizational actors, their practices and counterroles.

# Features
- Scrapes EIT news articles (2008–2025)

- Cleans and combines article texts

- Extracts role–practice–counterrole triplets using LLMs

- Builds an actor catalog with roles, founding dates, and locations

# Datasets
- Raw News Articles; Scraped from the official EIT website for the years 2008–2025. Stored year-wise in plain text files.

- Synthetic Dataset: Artificially generated dataset used for testing and evaluation of the triplet extraction pipeline.

# How to run

1. Clone the repository
   
    git clone https://github.com/stanley7/EIT-News-Triples.git
   
    cd EIT-News-Triples

3. Install dependencies
   
   pip install -r requirements.txt





