# source_generator.py
import requests
import json
import os
import re # Import regex for string cleaning and keyword extraction
import time # For adding a small delay to API calls

# --- Wikipedia API Configuration ---
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
API_CALL_DELAY = 0.1 # Small delay in seconds to be polite to the API

def clean_topic_title(title: str) -> str:
    """
    Cleans a topic title by removing common prefixes, articles, and pluralizations.
    Examples: "Introduction to HTML" -> "HTML"
              "The Hydrogen Atom" -> "Hydrogen Atom"
              "Basics of Quantum Mechanics" -> "Quantum Mechanics"
              "Matrices" -> "Matrix" (simple pluralization)
    """
    cleaned = title
    # Remove common prefixes (case-insensitive)
    prefixes = [
        r"Introduction to ",
        r"The ",
        r"An ",
        r"A ",
        r"Fundamentals of ",
        r"Basics of ",
        r"Advanced ",
        r"Concepts of "
    ]
    for prefix in prefixes:
        cleaned = re.sub(f"^{prefix}", "", cleaned, flags=re.IGNORECASE)
    
    cleaned = cleaned.strip()

    # Simple plural to singular (basic attempt, can be expanded)
    # Avoid removing 's' from words like 'physics', 'mathematics', 'analysis'
    if cleaned.lower().endswith("s") and len(cleaned) > 2 and not cleaned.lower().endswith("ss"):
        if not any(cleaned.lower().endswith(suffix) for suffix in ['ics', 'esis', 'us']):
            cleaned = cleaned[:-1]

    return cleaned

def extract_keywords_from_description(description: str) -> list:
    """
    Extracts potential sub-topic keywords/phrases from a description string.
    Assumes comma-separated or parenthetical phrases.
    """
    keywords = []
    # Find phrases within parentheses (e.g., "vector spaces, matrices, inner products")
    # or comma-separated lists outside of parentheses.
    
    # Split by common delimiters (comma, "and", list-like formatting)
    # Using regex to split by comma, semicolon, or " and " (with lookbehind to keep "and" if desired)
    parts = re.split(r'[;,]\s*|\s+and\s+', description)
    
    for part in parts:
        part = part.strip()
        if part:
            # Remove any trailing parentheses or periods if it's just a closing bracket
            part = re.sub(r'[\).\s]+$', '', part)
            # Remove leading parentheses if it's just an opening bracket
            part = re.sub(r'^\s*\(', '', part)
            
            if part and len(part) > 3: # Ignore very short keywords
                keywords.append(part)
                
    # Add an attempt to parse things like "Topic A: Subtopic1, Subtopic2"
    if ':' in description:
        post_colon = description.split(':', 1)[1].strip()
        more_parts = re.split(r'[;,]\s*|\s+and\s+', post_colon)
        for mp in more_parts:
            mp = mp.strip()
            if mp and len(mp) > 3 and mp not in keywords:
                keywords.append(mp)

    # Filter out common, less useful words if they become standalone keywords
    unwanted_keywords = ["etc", "and so on", "such as", "e.g.", "i.e.", "or", "introduction", "basics", "advanced"]
    keywords = [kw for kw in keywords if kw.lower() not in unwanted_keywords and len(kw.split()) <= 5] # Limit to 5 words per keyword for relevance
    
    return list(set(keywords)) # Return unique keywords


def search_wikipedia_article(query_term: str):
    """
    Searches Wikipedia for an article matching the query term,
    using a less strict approach by trying multiple search queries and
    checking for relevance.
    Returns the title and URL of the most relevant article found, or None.
    """
    search_queries_to_try = [query_term]
    
    # Add a cleaned version of the query term to search queries
    cleaned_query_term = clean_topic_title(query_term)
    if cleaned_query_term and cleaned_query_term.lower() != query_term.lower() and cleaned_query_term not in search_queries_to_try:
        search_queries_to_try.append(cleaned_query_term)
    
    # Also add a simplified version if it ends with "theory" or similar, just the core concept
    if query_term.lower().endswith(" theory"):
        core_concept = query_term.replace(" Theory", "", 1).replace(" theory", "", 1)
        if core_concept and core_concept.lower() != query_term.lower() and core_concept not in search_queries_to_try:
            search_queries_to_try.append(core_concept)

    found_articles = [] # List to store potential articles to evaluate

    for current_search_term in search_queries_to_try:
        params = {
            "action": "opensearch",
            "search": current_search_term,
            "limit": "10", # Get top 10 results for better chances
            "namespace": "0", # Search in main article namespace
            "format": "json"
        }
        try:
            # print(f"    Searching Wikipedia for: '{current_search_term}'") # Uncomment for verbose debugging
            response = requests.get(WIKIPEDIA_API_URL, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()

            # data format: [search_term, [titles], [descriptions], [urls]]
            if data and len(data) > 3 and len(data[1]) > 0:
                for i in range(len(data[1])):
                    title = data[1][i]
                    url = data[3][i]
                    
                    # --- Relevance Check ---
                    lower_query_term = current_search_term.lower()
                    lower_found_title = title.lower()

                    # Prioritize exact or near-exact matches based on query terms
                    if lower_query_term == lower_found_title:
                        # print(f"      Found exact match: '{title}' for '{query_term}'") # Uncomment for verbose debugging
                        return {"title": title, "url": url}

                    # Check for containment of the query term within the found title (or vice-versa)
                    if lower_query_term in lower_found_title or lower_found_title in lower_query_term:
                        # print(f"      Found strong containment match: '{title}' for '{query_term}'") # Uncomment for verbose debugging
                        return {"title": title, "url": url}

                    # Collect first result as a low-priority fallback if nothing better is found
                    if i == 0:
                        found_articles.append({"title": title, "url": url})

        except requests.exceptions.RequestException as e:
            print(f"Error searching Wikipedia for '{current_search_term}': {e}")
            continue # Try next query_term if one fails
        
        time.sleep(API_CALL_DELAY) # Be polite to Wikipedia API

    if found_articles:
        # If no strong match, return the best first result found from any query
        # print(f"    Returning first result as fallback: '{found_articles[0]['title']}' for '{query_term}'") # Uncomment for verbose debugging
        return found_articles[0]

    return None

def generate_sources_for_topic(topic_data: dict) -> list:
    """
    Generates a list of potential sources (URLs and basic info) for a given topic.
    Leverages both topic title and description for broader search.
    """
    sources = []
    seen_urls = set() # To store URLs and avoid duplicates
    
    topic_title = topic_data['title']
    topic_description = topic_data['description'] # Get the description

    print(f"  Searching sources for topic: '{topic_title}'")
    
    # 1. Search using the main topic title
    print(f"    - Main topic search: '{topic_title}'")
    wiki_info = search_wikipedia_article(topic_title)
    if wiki_info and wiki_info['url'] not in seen_urls:
        sources.append({
            "url": wiki_info['url'],
            "type": "Wikipedia Article",
            "title": wiki_info['title'],
            "relevance_score": 0.9,
            "context_for_topic": topic_title # Indicate this source is for the main topic
        })
        seen_urls.add(wiki_info['url'])
    elif not wiki_info:
        print(f"      No direct Wikipedia article found for main topic '{topic_title}'.")

    # 2. Extract keywords from description and search for each
    if topic_description:
        sub_topics = extract_keywords_from_description(topic_description)
        if sub_topics:
            print(f"    - Description sub-topics identified: {sub_topics}")
            for sub_topic in sub_topics:
                print(f"      - Sub-topic search: '{sub_topic}'")
                sub_wiki_info = search_wikipedia_article(sub_topic)
                if sub_wiki_info and sub_wiki_info['url'] not in seen_urls:
                    sources.append({
                        "url": sub_wiki_info['url'],
                        "type": "Wikipedia Article",
                        "title": sub_wiki_info['title'],
                        "relevance_score": 0.8, # Slightly lower relevance for sub-topics perhaps
                        "context_for_topic": sub_topic # Indicate which part of the description this source is for
                    })
                    seen_urls.add(sub_wiki_info['url'])
                elif not sub_wiki_info:
                    print(f"        No Wikipedia article found for sub-topic '{sub_topic}'.")
        else:
            print(f"    - No distinct sub-topics extracted from description.")

    return sources