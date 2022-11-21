from pdfminer.high_level import extract_text
from pathlib import Path
import re
import typer
from collections import defaultdict

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
    report_dict = defaultdict(list)
    for i, text in enumerate(cleaned_headers):
        header_count -= 1
        if header_count > 0:
            regex_string = re.escape(cleaned_headers[i]) + r'(.|\n)*?' + re.escape(cleaned_headers[i+1])
            main_body = re.search(regex_string, text_reduced).group()
        else:
            main_body = re.search(re.escape(cleaned_headers[i]) + r'(.|\n)*', text_reduced).group()
        addresses = ADDRESS_RE.findall(main_body)
        dates = DATE_RE.findall(main_body)
        descriptions = TEXT_AFTER_DATE_RE.findall(main_body)
        descriptions = [text.replace('\n', '') for text in descriptions]
        category = CATEGORY_RE.match(main_body)
        category_dict = {'category': category.group(), 'addresses': addresses, 'dates': dates, 'descriptions': descriptions}
        for key, value in category_dict.items():
            report_dict[key].append(value)
    print(len(report_dict['category']), len(report_dict['addresses']), len(report_dict['dates']), len(report_dict['descriptions']))
    return report_dict


if __name__ == '__main__':
    typer.run(extract_components)
