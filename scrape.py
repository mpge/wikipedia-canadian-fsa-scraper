import requests
from bs4 import BeautifulSoup
import re
import csv

VALID_START_LETTERS = ['A', 'B', 'C', 'E', 'G', 'H', 'J', 'K', 'L', 'M',
                       'N', 'P', 'R', 'S', 'T', 'V', 'X', 'Y']
BASE_URL = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_"

FSA_PATTERN = re.compile(r'^[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ]$')

def clean_region(tag):
    """Extract region text after the <b>FSA</b> tag in the same block."""
    texts = []
    sibling = tag.find_next_sibling()
    while sibling:
        text = sibling.get_text(" ", strip=True)
        if text:
            texts.append(text)
        sibling = sibling.find_next_sibling()
    return " ".join(texts).split(" ")[0] if texts else ""

def scrape_fsa_and_region():
    results = []

    for letter in VALID_START_LETTERS:
        url = BASE_URL + letter
        print(f"\n🔍 Scraping {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        count_before = len(results)

        # Check all <b> tags for FSA codes
        for bold in soup.find_all("b"):
            fsa = bold.get_text(strip=True).upper()

            if FSA_PATTERN.match(fsa) and fsa.startswith(letter):
                # Try to get region name from parent block
                region = ""
                parent = bold.find_parent(["td", "span", "div"])
                if parent:
                    # Try <a> tag
                    a = parent.find("a")
                    if a:
                        region = a.get_text(strip=True)
                    else:
                        # Fall back to text after the <b> tag
                        region = clean_region(bold)

                results.append((fsa, region))

        print(f"✅ Found {len(results) - count_before} FSAs for {letter}")

    return results

# Scrape data
fsa_region_pairs = scrape_fsa_and_region()

# Write to CSV
with open("canadian_fsas_with_regions.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["FSA", "Region"])
    writer.writerows(fsa_region_pairs)

print(f"\n📁 Saved {len(fsa_region_pairs)} FSAs with regions to canadian_fsas_with_regions.csv")
