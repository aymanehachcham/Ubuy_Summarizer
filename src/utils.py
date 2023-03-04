import logging
import re
from time import sleep

import numpy as np
import openai
import json
import os

from tqdm import tqdm

from components import UbuyProduct, AmazonProduct, UbuySettings, UbuyProductSummary
from openai.error import RateLimitError
import backoff

def preprocess_text(text:str):

    # remove special characters like [ ] ( ) { } < > / \ | ~ ` ! @ # $ % ^ & * - _ + = , . ? : ; ' "
    preprocessed = re.sub(r'[\[\](){}<>/\\|~`!@#$%^&*\-_+=,?:;\u2013\'\"]', '', text.lower())
    # remove the character ✔ using regex
    preprocessed = re.sub(r'✔', '', preprocessed)
    #remove all special symbols from string
    preprocessed =  re.sub(r'[^\w\s]', '', preprocessed)
    # remove multiple spaces
    preprocessed = re.sub(r'\s+', ' ', preprocessed)

    return preprocessed

# create a function to simulate a call to an api:
def gpt3_api_call(query: str):
    sleep(1)
    print(np.random.randint(0, 100))
    if np.random.randint(0, 10) % 3 == 0:
        raise RateLimitError()

    return f'This a simulated summary from gpt3. {query}'
    # return generate_summary_gpt3(query=quer

# split a paragraph into sentences using the pattern . after a word in upper case
def split_paragraph_into_sentences(paragraph: str):
    sentences = re.split(r'(?<=[.!?]) +', paragraph)
    return sentences

@backoff.on_exception(backoff.expo, openai.error.RateLimitError, max_time=120)
def generate_summary_gpt3(query: str):
    settings = UbuySettings()
    openai.api_key = settings.openapi_key

    # Set the model and prompt
    model_engine = "text-davinci-003"
    prompt = f"This is a description for an amazon product: {query}. I need a concise summary of 20 words explainig the main features of the product." \
             f"You need to use original words not present in the text to describe the product."

    # Set the maximum number of tokens to generate in the response
    max_tokens = 20

    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt.split(' ')[:4097],
        max_tokens=max_tokens,
        temperature=0.6,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Print the response
    return completion.choices[0].text

def run_amazon_data(raw_data_file:str):
    with open(raw_data_file, 'r') as file:
        data = json.load(file)

    all_amazon_products = []

    for d in data:
        if '|' in d['description']:
            d['description'] = preprocess_text(''.join(d['description'].split('|')[1:]))
            d['summary'] = generate_summary_gpt3(query=d['description'])
        try:
            all_amazon_products += [AmazonProduct(**d).copy().dict()]
        except ValueError:
            continue

    with open('../data_ubuy/amazon_descriptions.json', 'w') as file:
        json.dump(all_amazon_products, file, indent=4)

def run_ubuy_data(raw_data_file:str, output_file:str) -> None:
    logging.basicConfig(level=logging.INFO)
    with open(raw_data_file, 'r') as file:
        data = json.load(file)

    all_ubuy_products = []
    with tqdm(desc='Generating summary using GPT-3', total=len(data[:20])) as pbar:
        for idx, d in enumerate(data[:20]):
            try:
                d['summary'] = re.sub(r'\n\n', '', gpt3_api_call(query=d['description']))
                d['bullet_points'] = split_paragraph_into_sentences(d['summary'])
                all_ubuy_products += [UbuyProductSummary(**d).copy().dict()]
            except ValueError:
                continue
            except openai.error.OpenAIError:
                logging.info(f'OpenAIError: Files are saved in {output_file}')
                with open(f'../data_ubuy/{output_file}', 'w') as file:
                    json.dump(all_ubuy_products, file, indent=4)
                exit(1)

            pbar.update(1)
        with open(f'../data_ubuy/{output_file}', 'w') as file:
            json.dump(all_ubuy_products, file, indent=4)
        pbar.close()



def run_ubuy_data_without_summary(raw_data_file:str, output_file:str) -> None:
    with open(raw_data_file, 'r') as file:
        data = json.load(file)

    all_ubuy_products = []
    for d in data:
        d.pop('url')
        d.pop('specifications')

        d['name'] = preprocess_text(d['name'])
        d['description'] = preprocess_text(d['description'])
        d['short_description'] = preprocess_text(d['short_description'])

        try:
            all_ubuy_products += [UbuyProduct(**d).copy().dict()]
        except ValueError:
            continue

    with open(f'../data_ubuy/{output_file}', 'w') as file:
        json.dump(all_ubuy_products, file, indent=4)


# Join two json files
def join_files(file1:str, file2:str):
    with open(file1, 'r') as file:
        data1 = json.load(file)

    with open(file2, 'r') as file:
        data2 = json.load(file)

    data1 += data2

    with open('../data_ubuy/data.json', 'w') as file:
        json.dump(data1, file, indent=4)


# Transform a csv file to a json file:
def csv_to_json(csv_file:str):
    with open(csv_file, 'r') as file:
        data = file.readlines()
    # if there is the word amazon in the csv file name
    if 'amazon' in csv_file:
        data = [d.strip().split(',') for d in data]

        data = [
            {
            'name': d[1],
            'description': d[10],
            } for d in data[1:]
        ]

        with open('../data_ubuy/amazon.json', 'w') as file:
            json.dump(data, file, indent=4)

    if 'walmart' in csv_file:
        data = [d.strip().split(',') for d in data]

        data = [
            {
            'name': d[4],
            'description': d[20],
            } for d in data[1:]
        ]

        with open('../data_ubuy/walmart.json', 'w') as file:
            json.dump(data, file, indent=4)