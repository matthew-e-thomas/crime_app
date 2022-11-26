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

# response = requests.get(url)


# soup = BeautifulSoup(response.text, 'html.parser')
# Find all hyperlinks present on webpage
# links = soup.find_all('a')
#
# i = 0
#
# # From all links check for pdf link and
# # if present download file
# for link in links:
#     if ('.pdf' in link.get('href', [])):
#         i += 1
#         print("Downloading file: ", i)
#
#         # Get response object for link
#         response = requests.get(link.get('href'))
#
#         # Write content in pdf file
#         pdf = open("pdf"+str(i)+".pdf", 'wb')
#         pdf.write(response.content)
#         pdf.close()
#         print("File ", i, " downloaded")
#
# print("All PDF files downloaded")