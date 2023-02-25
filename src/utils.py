
import re
import openai
import json
from components import UbuyProduct, AmazonProduct

def preprocess_text(text:str):

    # remove special characters like [ ] ( ) { } < > / \ | ~ ` ! @ # $ % ^ & * - _ + = , . ? : ; ' "
    preprocessed = re.sub(r'[\[\](){}<>/\\|~`!@#$%^&*\-_+=,?:;\u2013\'\"]', '', text.lower())
    # remove the character ✔ using regex
    preprocessed = re.sub(r'✔', '', preprocessed)
    # remove multiple spaces
    preprocessed = re.sub(r'\s+', ' ', preprocessed)

    return preprocessed

# split a paragraph into sentences using the pattern . after a word in upper case
def split_paragraph_into_sentences(paragraph: str):
    sentences = re.split(r'(?<=[.!?]) +', paragraph)
    return sentences

def generate_summary_gpt3(query: str):
    # Replace YOUR_API_KEY with your OpenAI API key
    openai.api_key = "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"

    # Set the model and prompt
    model_engine = "text-davinci-003"
    prompt = f"This is a description for an amazon product: {query}. I need a concise summary of 100 words explainig the main features of the product." \
             f"You need to use original words not present in the text to describe the product."

    # Set the maximum number of tokens to generate in the response
    max_tokens = 100

    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
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

def run_ubuy_data(raw_data_file:str):
    with open(raw_data_file, 'r') as file:
        data = json.load(file)

    all_ubuy_products = []
    for d in data[:30]:
        d.pop('url')
        d.pop('specifications')

        d['name'] = preprocess_text(d['name'])
        d['description'] = preprocess_text(d['description'])
        d['short_description'] = preprocess_text(d['short_description'])
        d['summary'] = re.sub(r'\n\n', '', generate_summary_gpt3(query=d['description']))
        d['bullet_points'] = split_paragraph_into_sentences(d['summary'])

        try:
            all_ubuy_products += [UbuyProduct(**d).copy().dict()]
        except ValueError:
            continue

    with open('../data_ubuy/ubuy_descriptions_summary_2.json', 'w') as file:
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