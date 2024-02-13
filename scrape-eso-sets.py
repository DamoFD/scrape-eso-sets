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

set_names = []
for link in soup.select('td.d-none.d-xl-table-cell.align-middle a, span.d-xl-none a'):
    set_name = link.get_text(strip=True)
    set_names.append(set_name)

print(set_names)
