

from pydantic import BaseModel, validator
import re
import json
from typing import List
import openai

# generate text using openai library and gpt3
def generate_summary_gpt3(query: str):
    # Replace YOUR_API_KEY with your OpenAI API key
    openai.api_key = "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"

    # Set the model and prompt
    model_engine = "text-davinci-003"
    prompt = "I'm giving you a description for an amazon product. I want you to write a consise summary of no more than 60 words" \
             "using original words not present in the text, this is the product description: " + query

    # Set the maximum number of tokens to generate in the response
    max_tokens = 60

    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Print the response
    return completion.choices[0].text

class UbuyProduct(BaseModel):
    name: str
    short_description: str
    description: str
    summary:str

    class Config:
        allow_population_by_field_name = True

    @validator('short_description', 'description')
    def validate_description(cls, v):
        if v == '':
            raise ValueError(
                'Description cannot be empty'
            )

        if v == '[]':
            raise ValueError(
                'Invalid description'
            )

        # remove special characters like [ ] ( ) { } < > / \ | ~ ` ! @ # $ % ^ & * - _ + = , . ? : ; ' "
        preprocessed = re.sub(r'[\[\](){}<>/\\|~`!@#$%^&*\-_+=,?:;\'\"]', '', v)
        # remove the character ✔ using regex
        preprocessed = re.sub(r'✔', '', preprocessed)
        # remove multiple spaces
        preprocessed = re.sub(r'\s+', ' ', preprocessed)

        return preprocessed

class AmazonProduct(BaseModel):
    name: str
    description: str
    summary:str

    class Config:
        allow_population_by_field_name = True

    @validator('description', 'summary')
    def validate_description(cls, v):
        if v == '':
            raise ValueError(
                'Neither description nor summary can be empty'
            )
        return v

def preprocess_text(text:str):
    # remove special characters like [ ] ( ) { } < > / \ | ~ ` ! @ # $ % ^ & * - _ + = , . ? : ; ' "
    preprocessed = re.sub(r'[\[\](){}<>/\\|~`!@#$%^&*\-_+=,?:;\'\"]', '', text)
    # remove the character ✔ using regex
    preprocessed = re.sub(r'✔', '', preprocessed)
    # remove multiple spaces
    preprocessed = re.sub(r'\s+', ' ', preprocessed)

    return preprocessed

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

def run_ubuy_data(raw_data_file:str):
    with open(raw_data_file, 'r') as file:
        data = json.load(file)

    all_ubuy_products = []

    for d in data[:50]:
        d.pop('url')
        d.pop('specifications')
        d['summary'] = generate_summary_gpt3(query=d['description'])
        try:
            all_ubuy_products += [UbuyProduct(**d).copy().dict()]
        except ValueError:
            continue

    with open('../data_ubuy/ubuy_descriptions_summary.json', 'w') as file:
        json.dump(all_ubuy_products, file, indent=4)



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

if __name__ == '__main__':
    # csv_to_json(csv_file='../data_ubuy/walmart_sample.csv')
    # run_amazon_data(raw_data_file='../data_ubuy/amazon.json')
    run_ubuy_data(raw_data_file='../data_ubuy/descriptions.json')
    # print(generate_summary_gpt3(
    #     query='Each genie baby has a soft and cuddly body with genieinspired onesies with glitter detail. Girls can enjoy lots of fun hair play with their soft rooted Ponytails. These genie babies are the ideal size to give plenty of hugs and cuddles. Includes a matching jewel pacifier for nurture play. For ages 2 and up.'
    # ))