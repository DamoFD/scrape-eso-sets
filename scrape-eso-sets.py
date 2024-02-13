import requests
from bs4 import BeautifulSoup

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
    set = {"id": index, "name": name, "type": type, "slug": slug}
    sets.append(set)

print(sets)
