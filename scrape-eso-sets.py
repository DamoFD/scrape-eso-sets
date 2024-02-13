import requests
from bs4 import BeautifulSoup
import json

def get_info_from_url(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return "Failed to retrieve content, status code: {}".format(response.status_code)

url = 'https://www.eso-hub.com/en/sets/all'
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

                current_element = bonus

                while True:
                    current_element = current_element.next_element
                    if not current_element or current_element.name == 'strong':
                        break
                    if isinstance(current_element, str):
                        full_description += current_element.strip() + " "

                bonuses[item_count_key] = full_description.strip()

    set = {"id": index, "name": name, "type": type, "slug": slug, **bonuses}
    sets.append(set)

sets_json = json.dumps(sets, indent=4)

with open('eso.sets.json', 'w') as file:
    file.write(sets_json)
