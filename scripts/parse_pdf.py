from pdfminer.high_level import extract_text
from pathlib import Path
import re
import typer
from collections import defaultdict
import pandas as pd
from datetime import date, datetime

DATA_PATH = Path('../data/pdfs')
REPORT_PATH = Path(f'../data/csv_reports/crime_report_{date.today()}.csv')

CATEGORY_RE = re.compile(r'(.*)(?=:)')
ADDRESS_RE = re.compile(r'(\d{1,5}.+)(?=,\s\d)')
DATE_RE = re.compile(r'(\d{1,2}\/\d{1,2}).{1,3}(\d{1,2}\/\d{1,2})?')
TEXT_AFTER_DATE_RE = re.compile(r"(?<=\d,)\s*([^\.]*)")

def parse_pdf(file_path: Path) -> str:
    text = extract_text(file_path)
    return text


def extract_components(file_path: Path = DATA_PATH / 'crime_report_8.2.2022.pdf') -> dict:
    '''
    Uses regular expressions to extract dates, addresses, crime descriptions from the text
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
        for idx, date in enumerate(dates):
            if date[1] != '':
                datetime_range = pd.date_range(start=date[0] + '/2022', end=date[1] + '/2022').date.tolist()
                dates[idx] = datetime_range[0]
            else:
                dates[idx] = datetime.strptime(date[0] + '/2022', '%m/%d/%Y').date()
        descriptions = TEXT_AFTER_DATE_RE.findall(main_body)
        descriptions = [text.replace('\n', '') for text in descriptions]
        category = CATEGORY_RE.match(main_body).group()
        category_dict = {'category': category, 'address': addresses, 'date': dates, 'description': descriptions}
        for key, value in category_dict.items():
            report_dict[key].append(value)

    # print(report_dict)
    return report_dict

def create_csv() -> None:
    '''
    Creates a json schema from the dictionary of dates, addresses, and crime descriptions
    :param report_dict:
    :return: csv file
    '''
    report_dict = extract_components()
    df = pd.DataFrame(report_dict)
    df = df.explode(['address', 'date', 'description'])
    df.to_csv(REPORT_PATH, index=False, header=False)

if __name__ == '__main__':
    typer.run(create_csv)
