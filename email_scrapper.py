import pandas as pd

import regex as re
from bs4 import BeautifulSoup as bs
import requests

import os

def get_and_delete_file(folder_path):
    # List files in the folder
    files = os.listdir(folder_path)

    # Check if there are any files in the folder
    if len(files) == 0:
        print("No files found in the folder.")
        assert len(files) == 0

    # Get the first file in the folder
    file_name = files[0]
    file_path = os.path.join(folder_path, file_name)
    print(file_path)
    
    sample = pd.read_excel(file_path)

    # Delete the file
    os.remove(file_path)
    print(f"File '{file_name}' has been deleted.")
    return sample, file_name

def email_extract(query):
    # query = "Mediterranean Finance Ltd (LICENCE REVOKED ON 04/01/2024)"
    # query = "WeChat Pay Europe B.V."
    print(query)
    suffix = ["", " email", "support", "info", "contact", "address", "help"]
    
    links = []
    for addons in suffix:
        try:
            url = f"https://www.google.com/search?q={query+addons}&num=1&start=0"
            # print(url)
            r = requests.get(url, timeout=10)
            soup = bs(r.content)
            ## print(soup.prettify())

            pattern = r'url\?q(?!.*google).*?&amp;'

            # Find all matches
            matches = re.findall(pattern, soup.prettify())
            # print(matches)
            links.extend(list(set([match[6:-5] for match in matches])))
            
            # Print the matches
        except:
            continue
    
    links = list(set(links))
    
    group = []
    for link in links:
        try:
            # print(link)
            # print(match)
            #print(match[6:-5])
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

            r = requests.get(link, timeout=10)
            soup = bs(r.content)

            emails = list(set(re.findall(email_pattern, soup.prettify())))
            group.extend(emails)
        except:
            continue
        
    group = list(set(group))
    print(", ".join(group))
    print()
    return ", ".join(group)

def clean_emails(sample):
    sample = sample.split(", ")
    for samp in list(sample):
        if samp[-4:]=='.png':
            # print(samp)
            sample.remove(samp)


        elif samp[-4:]=='.svg':
            # print(samp)
            sample.remove(samp)

            
    return ", ".join(sample)

# from dask.distributed import Client
# import joblib
# client = Client(processes=False)        # create local clust


sample_200, file_name = get_and_delete_file("./split")
# with joblib.parallel_backend('dask'):   
sample_200["Email_address"] = sample_200['ENT_NAM'].apply(email_extract)
sample_200['Email_address'] = sample_200['Email_address'].apply(clean_emails)
sample_200.to_excel(f"./extracted/{file_name}", index=False)
