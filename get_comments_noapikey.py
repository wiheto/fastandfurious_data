#%%
import urllib.request, urllib.error
from bs4 import BeautifulSoup
import time 
import json
import pandas as pd
from datetime import datetime
import os
#%%
#Rundate March 19, 2024
apikey = 'NeedToFillInYourOwn' # Fill in Guardian API key here.
apiq = f'https://content.guardianapis.com/search?&api-key={apikey}&page-size=200&show-fields=shortUrl&long-domain-short-url=true&show-tags=keyword'
#%%
# add section
sections = ['commentisfree']

section = sections[0]
apiq = apiq + f'&section={section}'


#%%
# 2005 to 2024
for year in range(2005, 2025):
    print(year)
    article_url_base = apiq + f'&from-date={year}-01-01' + f'&to-date={year}-12-31'
    with urllib.request.urlopen(article_url_base) as response:
        data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
    total_pages = data['response']['pages']

    for page in range(1, total_pages+1):
        article_url = article_url_base + f'&page={page}'
        with urllib.request.urlopen(article_url) as response:
            data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
        for n in data['response']['results']:
            n['shortUrl'] = n['fields']['shortUrl'].split('.com')[1]
            tags=set(list([t['webTitle'] for t in n['tags']]))
            n['tags'] = ', '.join(tags)

        df = pd.DataFrame(data['response']['results'])
        df.to_csv(f'./data/article_urls/{section}/{year}_{page}.csv')
        time.sleep(2)

#%%
files = sorted(os.listdir(f'./data/article_urls/{section}'))
short_urls = []
for f in files: 
    print(f)
    df = pd.read_csv(f'./data/article_urls/{section}/{f}', index_col=[0])
    short_urls.extend(df['shortUrl'].tolist())


#%%
s = 0 # If need to restart, change this as progression is saved. 
for i, url in enumerate(short_urls[s:]):
    print(str(i+s) + ' - ' + url)
    sname = url.split('/')[-1]
    os.makedirs(f'./data/raw/{sname}/', exist_ok=True)
    page = 1 
    all_pages = False
    comments_url = f'https://discussion.guardianapis.com/discussion-api/discussion/{url}?orderBy=oldest&pageSize=100&page={page}&api-key={apikey}'
    if os.path.exists(f'./data/raw/{sname}/1.json'):
        data = json.load(open(f'./data/raw/{sname}/1.json'))
        total_pages = data['pages']
    # check if HTTP Error
    else:            
        try:
            with urllib.request.urlopen(comments_url) as response:
                data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
            total_pages = data['pages']
        # If no discussion seciton it will raise a 404 error
        except urllib.error.HTTPError as e:
            print('HTTPError: {}'.format(e.code))
            total_pages = 0
            time.sleep(3)
    for page in range(1, total_pages+1):
        if os.path.exists(f'./data/raw/{sname}/{page}.json'):
            continue
        else:
            comments_url = f'https://discussion.guardianapis.com/discussion-api/discussion/{url}?orderBy=oldest&pageSize=100&page={page}&api-key={apikey}'
            with urllib.request.urlopen(comments_url) as response:
                data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
            with open(f'./data/raw/{sname}/{page}.json', 'w') as f:
                json.dump(data, f)
            time.sleep(1)



    # %%
