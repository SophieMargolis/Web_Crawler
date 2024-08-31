import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

class WebCrawler:

    def __init__(self, main_url):
        '''
        Initialize the WebCrawler with the main URL to crawl.
        
        :param main_url: The URL of the main page to start crawling from.
        '''

        self.main_url = main_url
        self.page_data = [] # List to store data of crawled pages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def extract_page_data(self, url):
        '''
        Extract the title, URL, and body content of a given page.
        
        :param url: The URL of the page to extract data from.
        :return: A tuple containing the page title, URL, and body content.
        '''

        try:
            # Send HTTP GET request to the URL
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract page title
            title = soup.title.string if soup.title else 'No Title'
            
            # Remove all meta tags and non-body content
            for meta in soup.find_all('meta'):
                meta.decompose()
            for header in soup.find_all(['header', 'nav', 'aside']):
                header.decompose()
            
            # Extract and clean the body content
            body = soup.find('body')
            if body:
                content = body.get_text(separator=' ', strip=True)
            else:
                content = 'No Body Content'
            
            return title, url, content
        
        except Exception as e:
            print(f"Failed to retrieve {url}: {e}")
            return None, None, None

    def crawl(self):
        '''
        Crawl the main page and its links to collect data.
        '''

        # Crawl the main page
        title, url, content = self.extract_page_data(self.main_url)
        if title and url and content:
            self.page_data.append((title, url, content))

        try:
            # Parse the main page and find all the links
            response = requests.get(self.main_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all anchor tags with href attributes
            links = soup.find_all('a', href=True)
            
            # Iterate over the 11 links (which are all the links on the website) and convert relative URLs to absolute URLs
            for link in links[:11]:
                full_url = urljoin(self.main_url, link['href'])  
                
                # Extract data from the linked page
                title, url, content = self.extract_page_data(full_url)
                if title and url and content:
                    self.page_data.append((title, url, content))

        except Exception as e:
            print(f"Failed to crawl {self.main_url}: {e}")

    def save_to_excel(self, file_name='crawled_data.xlsx'):
        '''
        Save the collected page data to an Excel file.
        
        :param file_name: The name of the Excel file to save the data to.
        '''

        # Convert to pandas df and save it to an excel file
        df = pd.DataFrame(self.page_data, columns=['Page Name', 'Page URL', 'Page Content'])
        df.to_excel(file_name, index=False)
#        print(f"Data saved to {file_name}")

if __name__ == "__main__":
    crawler = WebCrawler(main_url="https://www.hapoeluta.org/")
    crawler.crawl()
    crawler.save_to_excel()
