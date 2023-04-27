from bs4 import BeautifulSoup
from text import text
import aiohttp
import asyncio
import pandas as pd

# Parse HTML text and extract links
soup = BeautifulSoup(text, 'html.parser')
links = soup.select('.nd-kategori a')
links = ['https://www.klikindomaret.com' + link['href'] for link in links]

# List to store scraped data
all_data = []

async def parsing(session, url):
    """
    A coroutine function to parse a given URL and extract product information.

    Args:
        session: aiohttp.ClientSession object for making HTTP requests.
        url: A string representing the URL to be scraped.

    Returns:
        None
    """
    # Extract category from URL
    cat = url.split('/')[-1]

    # Make HTTP request to URL and parse response
    async with session.get(url) as response:
        print(response.status, url)
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')

        # Loop through product items on page and extract data
        for i in soup.find_all('div', {'class': 'item'}):
            try:
                product_name = i.find('div', {'class': 'title'}).text.strip()
                product_price = i.find('span', {'class': 'normal price-value'}).text.strip()
                all_data.append({'product_name':product_name, 'product_price':product_price, 'product_category':cat})
            except:
                # Skip product if data extraction fails
                pass

async def fetch_content(semaphore, session, url):
    """
    A coroutine function to fetch content from a given URL using a semaphore to limit concurrent requests.

    Args:
        semaphore: asyncio.Semaphore object to limit number of concurrent requests.
        session: aiohttp.ClientSession object for making HTTP requests.
        url: A string representing the URL to be scraped.

    Returns:
        None
    """
    async with semaphore:
        await parsing(session, url)

async def main():
    """
    The main coroutine function to coordinate scraping of all URLs and write results to an Excel file.

    Args:
        None

    Returns:
        None
    """
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(5)

    # Create aiohttp.ClientSession object for making HTTP requests
    async with aiohttp.ClientSession() as session:
        # Create list of tasks to fetch content from all URLs
        tasks = [fetch_content(semaphore, session, url) for url in links]
        # Run all tasks concurrently using asyncio.gather
        await asyncio.gather(*tasks)

# Run main function to scrape all data and write to Excel file
asyncio.run(main())
pd.DataFrame(all_data).to_excel('data_scrapping.xlsx')

# Print message to indicate completion of program
print('done...')
