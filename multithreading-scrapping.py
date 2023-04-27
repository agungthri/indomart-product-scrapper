# Import necessary libraries
from bs4 import BeautifulSoup
from text import text
import requests
import concurrent.futures
import pandas as pd
from typing import List, Dict

# Use BeautifulSoup to parse the HTML text
soup = BeautifulSoup(text, 'lxml')

# Extract all the category links from the HTML
links = soup.select('.nd-kategori a')
# Append the base URL to each link
links = set(['https://www.klikindomaret.com' + link['href'] for link in links])

# Create an empty list to store all the scraped data
all_data: List[Dict[str, str]] = []

def parsing(url: str) -> None:
    """
    Scrapes data from a single URL and appends it to the all_data list.

    Parameters:
        url (str): The URL to scrape data from.

    Returns:
        None
    """
    # Extract the category name from the URL
    cat = url.split('/')[-1]
    # Make a request to the URL
    response = requests.get(url)
    # Print the response status code and URL for debugging purposes
    print(response.status_code, url)
    # Get the HTML content of the response
    content = response.text
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(content, 'lxml')
    # Loop through each item in the HTML and extract the product name and price
    for i in soup.find_all('div', {'class': 'item'}):
        try:
            product_name = i.find('div', {'class': 'title'}).text.strip()
            product_price = i.find('span', {'class': 'normal price-value'}).text.strip()
            # Add the product name, price, and category to the all_data list
            all_data.append({'product_name':product_name, 'product_price':product_price, 'product_category':cat})
        except:
            # If an error occurs while scraping, skip the item and continue to the next one
            pass

def fetch_content(url: str) -> None:
    """
    Fetches content from a URL using multiple threads.

    Parameters:
        url (str): The URL to fetch content from.

    Returns:
        None
    """
    # Call the parsing function to scrape data from the URL
    parsing(url)

if __name__ == '__main__':
    # Use a ThreadPoolExecutor to fetch content from multiple URLs concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit each URL to the executor and store the future task in a dictionary
        future_tasks = {executor.submit(fetch_content, url): url for url in links}
        # Wait for all the tasks to complete and handle any exceptions that occur
        for future in concurrent.futures.as_completed(future_tasks):
            url = future_tasks[future]
            try:
                future.result()
            except Exception as exc:
                print(f'Error occurred while scraping {url}: {exc}')

    # Convert the scraped data to a pandas DataFrame and save it to an Excel file
    pd.DataFrame(all_data).to_excel('data_scrapping.xlsx')
    # Print a message to indicate that the scraping is done
    print('done...')
