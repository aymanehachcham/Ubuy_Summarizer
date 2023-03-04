
from pydantic import parse_obj_as
from utils import run_ubuy_data, csv_to_json, join_files, run_ubuy_data_without_summary, generate_summary_gpt3
import re

if __name__ == '__main__':
    # run_ubuy_data_without_summary(raw_data_file='../data_ubuy/data.json',
    #                               output_file='data_no_summary.json')
    run_ubuy_data(raw_data_file='../data_ubuy/data_no_summary.json',
                  output_file='data_summary.json')
    # print(generate_summary_gpt3('Hello World'))
