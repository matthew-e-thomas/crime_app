from pdfminer.high_level import extract_text
from pathlib import Path
import re
import typer
from collections import defaultdict
from pandas import date_range, DataFrame
from datetime import datetime
from unicodedata import normalize

DATA_PATH = Path('../data/pdfs')
REPORT_PATH = Path('../data/csv_reports/')

CATEGORY_RE = re.compile(r'(.*):(?!\S)')
ADDRESS_RE = re.compile(r'(\d*.+),\s*\d{1,2}/')
DATE_RE = re.compile(r'(\d{1,2}\/\d{1,2}).{1,3}(\d{1,2}\/\d{1,2})?')
TEXT_AFTER_DATE_RE = re.compile(r"\d,([^.]+)")


def parse_pdf(file_path: Path) -> str:
    text = extract_text(file_path)
    return text


def extract_components(file_path: Path) -> dict:
    """
    Uses regular expressions to extract dates, addresses, crime descriptions from the text
    :param file_path: path to pdf file
    :return: dictionary of dates, addresses, and crime descriptions
    """
    text = parse_pdf(file_path)

    text_reduced = re.sub(r'Arrests:((.|\n)*)', '', text)   # remove arrests
    text_reduced = re.sub(r'(Crime.*)', '', text_reduced)
    text_norm = normalize('NFKD', text_reduced)
    text_norm = re.sub(r'\d{1,2}:\d{2}\s*[AaPp]\.?[Mm]\.?', '', text_norm)      #remove times
    headers = re.findall(CATEGORY_RE, text_norm)         # find headers
    cleaned_headers = [header.strip() for header in headers if header != '']
    header_count = len(cleaned_headers)
    report_dict = defaultdict(list)
    for i, text in enumerate(cleaned_headers):
        header_count -= 1
        if header_count > 0:
            regex_string = re.escape(cleaned_headers[i]) + r'(.|\n)*?' + re.escape(cleaned_headers[i+1])
            main_body = re.search(regex_string, text_norm).group()
        else:
            main_body = re.search(re.escape(cleaned_headers[i]) + r'(.|\n)*', text_norm).group()
        addresses = ADDRESS_RE.findall(main_body)
        if not addresses:
            addresses = ['']
        dates = DATE_RE.findall(main_body)
        for idx, date in enumerate(dates):
            if date[1] != '':
                datetime_range = date_range(start=date[0] + '/2022', end=date[1] + '/2022').date.tolist()
                dates[idx] = datetime_range[0]
            else:
                dates[idx] = datetime.strptime(date[0] + '/2022', '%m/%d/%Y').date()
        descriptions = TEXT_AFTER_DATE_RE.findall(main_body)
        descriptions = [text.replace('\n', '') for text in descriptions]
        category = cleaned_headers[i]
        category_dict = {'category': category, 'address': addresses, 'date': dates, 'description': descriptions}
        for key, value in category_dict.items():
            report_dict[key].append(value)

    # print(report_dict)
    return report_dict


def create_csv(report_path: Path = typer.Argument(REPORT_PATH / 'crime_report_2022-9-19.csv'),
               data_path: Path = typer.Argument(DATA_PATH / '9.19.2022.pdf')) -> None:
    """
    Creates a csv file from the dictionary of dates, addresses, and crime descriptions
    :param report_path: path to the csv of parsed data
    :param data_path: path to the pdf taken from the website
    :return: csv file
    """
    report_dict = extract_components(data_path)
    df = DataFrame(report_dict)
    df = df.explode(['address', 'date', 'description']) # separate lists into rows since each header may have several crime descriptions
    df = df.dropna()
    df.to_csv(report_path, index=False)


if __name__ == '__main__':
    typer.run(create_csv)
