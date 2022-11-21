from pdfminer.high_level import extract_text
from pathlib import Path
import re
import typer

DATA_PATH = Path('../data')

CATEGORY_RE = re.compile(r'(.*)(?=:)')
ADDRESS_RE = re.compile(r'\d{1,5}[\s\w]+(?=,\s\d)')
DATE_RE = re.compile(r'(\d{1,2}\/\d{1,2}).{3}(\d{1,2}\/\d{1,2})?')
TEXT_AFTER_DATE_RE = re.compile(r"(?<=\d,)\s*([^\.]*)")

def parse_pdf(file_path: Path) -> str:
    text = extract_text(file_path)
    return text


def extract_components(file_path: Path = DATA_PATH / 'crime_report_8.2.2022.pdf') -> dict:
    '''
    Uses regular expressions to extract dates and addresses from the text
    :param text:
    :return: dictionary of dates and addresses
    '''
    text = parse_pdf(file_path)

    text_reduced = re.sub(r'Arrests:((.|\n)*)', '', text)   # remove arrests
    text_reduced = re.sub(r'(Crime.*)', '', text_reduced)
    headers = re.findall(CATEGORY_RE, text_reduced)         # find headers
    cleaned_headers = [header.strip() for header in headers if header != '']
    header_count = len(cleaned_headers)
    for i, text in enumerate(cleaned_headers):
        header_count -= 1
        if header_count > 0:
            regex_string = re.escape(cleaned_headers[i]) + r'(.|\n)*?' + re.escape(cleaned_headers[i+1])
            main_body = re.search(regex_string, text_reduced).group()
        else:
            main_body = re.search(re.escape(cleaned_headers[i]) + r'(.|\n)*', text_reduced).group()
        print(main_body)
    # addresses = ADDRESS_RE.findall(text_reduced)
    # dates = DATE_RE.findall(text_reduced)
    # descriptions = TEXT_AFTER_DATE_RE.findall(text_reduced)
    # descriptions = [text.replace('\n', '') for text in descriptions]
    # categories = CATEGORY_RE.findall(text_reduced)
    # report_dict = {'category': categories, 'addresses': addresses, 'dates': dates, 'descriptions': descriptions}
    # print (len(dates), len(addresses), len(descriptions), len(categories))
    # print(addresses)
    # return report_dict


if __name__ == '__main__':
    typer.run(extract_components)
