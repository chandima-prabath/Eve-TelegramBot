import requests
from bs4 import BeautifulSoup

def extract_original_image_urls(url):
    try:
        # Make a GET request to fetch the raw HTML content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the content of the request with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all img tags within the specified div structure
        image_tags = soup.find_all('div', class_='list-item-image fixed-size')

        # Extract original image URLs from img tags
        original_image_urls = []
        for img_tag in image_tags:
            image_url = img_tag.find('img')['src']
            original_image_urls.append(image_url)

        return original_image_urls

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

# Example usage:
if __name__ == "__main__":
    base_url = 'https://unicone-studio.imgbb.com/'
    image_urls = extract_original_image_urls(base_url)
    for url in image_urls:
        print(url)
