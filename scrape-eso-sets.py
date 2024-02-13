import requests
from bs4 import BeautifulSoup
import json
import re
import time

def get_info_from_url(url):
    response = requests.get(url, headers={'User-Agent': 'ESOCrawler/1.0'})

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve content from {url}, status code: {response.status_code}")
        return None

def parse_set_details_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    set_pieces = [span.get_text() for span in soup.select('span.badge.badge-info')]
    location_strong_tag = soup.find('strong', text='Location:')
    locations_list = location_strong_tag.find_next_sibling('ul') if location_strong_tag else None
    locations = [a.get_text() for a in locations_list.find_all('a')] if locations_list else []
    return set_pieces, locations

def fetch_all_sets(url):
    html_content = get_info_from_url(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    sets = []

    for index, row in enumerate(soup.select('tr'), start=1):
        link_element = row.select_one('td.d-none.d-xl-table-cell.align-middle a, span.d-xl-none a')
        name = link_element.get_text(strip=True)
        href = link_element['href']

        slug = href.split('/')[-1]

        type = row.select_one('small').get_text(strip=True) if row.select_one('small') else "Unknown Type"

        # Find all bonuses for this set
        bonuses = {'1_item': None, '2_items': None, '3_items': None, '4_items': None, '5_items': None}

        bonuses_container = row.select_one('td:last-child')
        if bonuses_container:

            for bonus in bonuses_container.find_all('strong', class_='set-bonus'):
                bonus_text = bonus.get_text(strip=True)
                if bonus_text:
                    item_count = bonus_text.split(' ')[0].replace('(', '').replace(')', '')
                    item_count_key = f"{item_count}_item" if item_count == "1" else f"{item_count}_items"

                    full_description=""
                    for sibling in bonus.next_siblings:
                        if sibling.name == 'strong':
                            break
                        if sibling.name == 'br':
                            continue
                        if sibling.string:
                            full_description += sibling.string.strip() + " "
                        elif sibling.name == 'span':
                            full_description += sibling.get_text(strip=True) + " "

                    clean_description = re.sub(r'\s+', ' ', full_description.strip())

                    bonuses[item_count_key] = clean_description

        set = {"id": index, "name": name, "type": type, "slug": slug, **bonuses}
        sets.append(set)
    return sets

def enrich_sets_with_details(sets):
    base_url = "https://www.eso-hub.com/en/sets/"
    for set in sets:
        slug = set["slug"]
        url = f"{base_url}{slug}"
        html_content = get_info_from_url(url)
        if html_content:
            set_pieces, locations = parse_set_details_page(html_content)
            set["set_pieces"] = set_pieces
            set["locations"] = locations
            time.sleep(1)

def main():
    all_sets_url = 'https://www.eso-hub.com/en/sets/all'
    sets = fetch_all_sets(all_sets_url)
    enrich_sets_with_details(sets)

    sets_json = json.dumps(sets, indent=4)
    with open('eso.sets-locations.json', 'w') as file:
        file.write(sets_json)

if __name__ == "__main__":
    main()
