import requests
from bs4 import BeautifulSoup

def search(query):
    url = f"https://www.google.com/search?q={query} site:allrecipes.com"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    search_results = soup.find_all('a')

    recipe_url = None
    for link in search_results:
        link_url = link.get('href')
        if link_url.startswith('/url?q=https://www.allrecipes.com/recipe/') and 'search' not in link_url:
            recipe_url = link_url.split('&')[0][7:]
            break

    if not recipe_url:
        return {'error_message': 'No recipe found.'}

    recipe_page = requests.get(recipe_url)
    recipe_soup = BeautifulSoup(recipe_page.content, 'html.parser')

    # Extract the image URL
    image_element = recipe_soup.find('div', class_='img-placeholder').find('img')
    image_url = image_element.get('data-src')

    return {'image_url': image_url}


if __name__ == "__main__":
    # Test the search function with a sample query
    query = "chocolate chip cookies"  # Replace with your desired query
    result = search(query)

    if 'image_url' in result:
        print(f"Image URL for '{query}': {result['image_url']}")
    elif 'error_message' in result:
        print(f"Error: {result['error_message']}")
    else:
        print("No image URL or error found.")

