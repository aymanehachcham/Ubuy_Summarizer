
from pydantic import parse_obj_as
from utils import run_ubuy_data, csv_to_json
import re

if __name__ == '__main__':
    run_ubuy_data(raw_data_file='../data_ubuy/descriptions.json')


