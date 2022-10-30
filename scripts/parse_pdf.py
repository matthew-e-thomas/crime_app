from pdfminer.high_level import extract_text
from pathlib import Path
import re
import typer

DATA_PATH = Path('../data')


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
    ADDRESS_RE = re.compile(r'\d{1,5}[\s\w]*(?=,)')
    DATE_RE = re.compile(r'\d{1,2}\/\d{1,2}')
    TEXT_AFTER_DATE_RE = re.compile(r"(?<=\d{1},)[^,]*$")
    addresses = ADDRESS_RE.findall(text)
    dates = DATE_RE.findall(text)
    descriptions = TEXT_AFTER_DATE_RE.findall(text)
    report_dict = {'addresses': addresses, 'dates': dates, 'descriptions': descriptions}
    print(report_dict)
    return report_dict


if __name__ == '__main__':
    typer.run(extract_components)
