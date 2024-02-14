import requests
from bs4 import BeautifulSoup
import os
import json

def get_info_from_url(url):
    response = requests.get(url, headers={'User-Agent': 'ESOCrawler/1.0'})

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve content from {url}, status code: {response.status_code}")
        return None

def fetch_set_images(url):
    html_content = get_info_from_url(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    sets = []

    for index, row in enumerate(soup.select('tr'), start=1):
        img_element = row.select_one('.set-icon')
        if img_element:
            src = img_element['src']
            img_name = os.path.basename(src)
            set = {"id": index, "img": img_name}
            sets.append(set)
    return sets

def update_sets_with_images(sets, images):
    image_mapping = {image['id']: image['img'] for image in images}

    for set in sets:
        set_id = set['id']
        if set_id in image_mapping:
            set['image'] = image_mapping[set_id]

def main():
    with open('eso.sets-locations-images.json', 'r') as file:
        sets = json.load(file)

    all_sets_url = 'https://www.eso-hub.com/en/sets/all'
    images = fetch_set_images(all_sets_url)

    update_sets_with_images(sets, images)

    with open('eso.sets-locations-images.json', 'w') as file:
        json.dump(sets, file, indent=4)

if __name__ == '__main__':
    main()
