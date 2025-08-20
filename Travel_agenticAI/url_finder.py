import os
from googlesearch import search
import time
import re

# --- 1. Configuration ---
# Define the countries/topics you want to find travel guides for.
SEARCH_TOPICS = [
    "Spain",
    "France",
    "Italy",
    "Japan",
    "Thailand",
    "Australia", 
    "India",
    "Pakistan",
    "Srilanka",
    "America"
]

# Define the search query templates.
QUERY_TEMPLATES = [
    "{topic} travel guide",
    "things to do in {topic}",
    "{topic} itinerary",
    "best travel blog {topic}"
]

# The target file to update.
TARGET_FILE = "gather_knowledge.py"
NUM_RESULTS_PER_QUERY = 5 # Number of URLs to fetch per search query.

# --- 2. The URL Finding Function ---
def find_travel_urls(topics, templates, num_results):
    """
    Searches Google for travel-related URLs based on topics and templates.
    """
    all_urls = set() # Use a set to automatically handle duplicates.
    print(f"--- Starting URL search for {len(topics)} topics... ---")

    for topic in topics:
        print(f"\nSearching for topic: {topic}")
        for template in templates:
            query = template.format(topic=topic)
            print(f"  > Performing search: '{query}'")
            try:
                # The 'stop' parameter controls how many results to fetch.
                # The 'pause' is crucial to avoid getting blocked by Google.
                results = search(query, stop=num_results, pause=2.0)
                
                for url in results:
                    # Basic filtering to avoid irrelevant sites.
                    if "youtube.com" not in url and "booking.com" not in url and "tripadvisor.com" not in url:
                        all_urls.add(url)
                
                # A longer pause between different search queries.
                time.sleep(5)

            except Exception as e:
                print(f"  > An error occurred during search: {e}")
                print("  > Continuing to next search...")
                time.sleep(10) # Wait longer after an error.

    return list(all_urls)

# --- 3. The File Update Function ---
def update_scraper_file(filepath, url_list):
    """
    Dynamically updates the URLS_TO_SCRAPE list in the target Python file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Format the list of URLs into a string that looks like Python code.
        url_list_str = "[\n"
        for url in url_list:
            url_list_str += f'    "{url}",\n'
        url_list_str += "]"

        # Use regex to find and replace the old URLS_TO_SCRAPE list.
        # This is more robust than simple string replacement.
        new_content = re.sub(
            r'URLS_TO_SCRAPE\s*=\s*\[.*?\]',
            f'URLS_TO_SCRAPE = {url_list_str}',
            content,
            flags=re.DOTALL
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n--- Successfully updated {filepath} with {len(url_list)} URLs. ---")

    except FileNotFoundError:
        print(f"Error: The target file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred while updating the file: {e}")

# --- 4. Main Execution ---
if __name__ == "__main__":
    # Step 1: Install the required library if you haven't already.
    # You can run this in your terminal: pip install googlesearch-python
    
    # Step 2: Find the URLs.
    found_urls = find_travel_urls(SEARCH_TOPICS, QUERY_TEMPLATES, NUM_RESULTS_PER_QUERY)
    
    # Step 3: Update the gather_knowledge.py script.
    if found_urls:
        update_scraper_file(TARGET_FILE, found_urls)
    else:
        print("--- No URLs found. The target file was not updated. ---")
