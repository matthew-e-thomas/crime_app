import requests
from bs4 import BeautifulSoup
import typer

# URL from which pdfs to be downloaded
POLICE_URL = "https://www.fredericksburgva.gov/1426/Crime-Reports"


def download_pdfs(url: str = POLICE_URL) -> None:
    '''
    Downloads pdfs from the url
    :param url:
    :return: None
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    pdfs = soup.find_all('a', href=True)
    for pdf in pdfs:
        if pdf['href'].endswith('.pdf'):
            print(pdf['href'])
            pdf_url = url + pdf['href']
            r = requests.get(pdf_url, allow_redirects=True)
            doc = open(pdf['href'], 'wb')
            doc.write(r.content)
            doc.close()
    print('Done')

if __name__ == '__main__':
    typer.run(download_pdfs)
