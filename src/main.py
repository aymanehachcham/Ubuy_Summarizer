
from pydantic import parse_obj_as
from components import run_ubuy_data, csv_to_json

if __name__ == '__main__':
    run_ubuy_data(raw_data_file='../data_ubuy/descriptions.json')
    csv_to_json(csv_file='../data_ubuy/amazon.csv')
