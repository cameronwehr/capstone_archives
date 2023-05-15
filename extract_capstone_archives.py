import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Input URL and output the data from the Capstone Archives
def extract_info(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        divisions, subdivisions, e_records, folders, authors, titles, abstracts, year_date = [],[],[],[],[],[],[],[]

        for row in soup.find('table').find_all('tr'):
            if row.has_attr('class'):
                if row['class'][0] == 'series':
                    division = row.text.strip()
                elif row['class'][0] == 'subseries':
                    subdivision = row.text.strip()
                elif (row['class'][0] == 'even_row') or (row['class'][0] == 'odd_row'):
                    e_record = row.find('td', class_='container')
                    folder = e_record.find_next()
                    author_title = folder.find_next(class_='unittitle')
                    author = author_title.text.strip().split('.')[0]
                    title = author_title.text.strip().split('.')[1]
                    scope_title = author_title.find_next('p')
                    abstract = scope_title.find_next('p')
                    year = abstract.find_next('td')

                    divisions.append(division)
                    subdivisions.append(subdivision)
                    e_records.append(e_record.text.strip())
                    folders.append(folder.text.strip())
                    authors.append(author)
                    titles.append(re.sub(' +', ' ', title.text.strip()))
                    abstracts.append(re.sub(' +', ' ', abstract.text.strip()))
                    year_date.append(year.text.strip())
            else:
                continue
    else:
        print("Failed to retrieve the web page.")

    df = pd.DataFrame({
        'Division': divisions,
        'Subdivision': subdivisions,
        'E-Record': e_records,
        'Folder': folders,
        'Author(s)': authors,
        'Title': titles,
        'Abstract': abstracts,
        'Year': year_date,
    })
    
    return df.drop_duplicates()

# Use the above scraping function on following URLs, create a dataframe with all data
# URLs
engineering_url = "http://dlib.nyu.edu/findingaids/html/nyuad/ad_mc_004/dscaspace_76b01eb87c7a80289e06bbdd3f316aa9.html" 
arts_url = "http://dlib.nyu.edu/findingaids/html/nyuad/ad_mc_004/dscaspace_b5939723c04fff5abff3b8b121908017.html"
sciences_url = "http://dlib.nyu.edu/findingaids/html/nyuad/ad_mc_004/dscaspace_840d11fce9c522905997a4cc34a63afa.html"
social_sciences_url = "http://dlib.nyu.edu/findingaids/html/nyuad/ad_mc_004/dscaspace_209570724935ccbb44e160486e10ab1b.html"

dfs = []
for i in [engineering_url, arts_url, sciences_url, social_sciences_url]:
    this_df = extract_info(i)
    dfs.append(this_df)
    
# Output as a dataframe
df = pd.concat(dfs).drop_duplicates().reset_index(drop=True)