import requests
import pandas as pd
from lxml import etree
from datetime import datetime
from hashlib import md5
import json
import time


def change_date(dateStr):
    input_format = '%a, %d %b %Y %H:%M:%S %z'
    output_format = '%Y-%m-%d'

    new_data = datetime.strptime( \
        dateStr, \
        input_format).strftime(output_format)

    return new_data


def encrypt_md5(str_josn):
    # create md5 object
    new_md5 = md5()
    # have to use .encode() or it will show TypeError: Unicode-objects must be encoded before hashing
    new_md5.update(str_josn.encode(encoding='utf-8'))
    # encrypt
    return new_md5.hexdigest() 


def get_cnn(keywords):
    """get cnn data"""

    # save the data 
    data = []
    # remove id deplicate
    id_set = set()
    for keyword in keywords:
        index = 1
        year = 2022  #starting year
        pre_rst_md5= ""
        while year>=2005: 
            url = f"https://search.api.cnn.com/content?q={keyword}&size=50&from={(index -1 )*10}&page={index}&sort=newest"
            res = requests.get(url)
            rst = res.json()['result']
            
            rst_json = json.dumps(rst)
            curr_rst_md5 = encrypt_md5(rst_json)

            #get data
            for item in rst:
                try:
                    id = item['_id']
                    if id in id_set:
                        continue
                    news_year = int(item["lastPublishDate"][:4])
                    if news_year > 2022:
                        continue
                    id_set.add(id)
                    data.append(
                        {
                            "keyword":keyword,              #keyword    
                            "url":item["url"],              #link
                            "from" : 'cnn',
                            "headline": item["headline"],   #title
                            "body": item["body"],           #content
                            "body_word_count" : len(item["body"].split()),   #word count
                            "date" : item["lastPublishDate"][:10]                   #publish date
                        }

                    )
                    
                except Exception as e:
                    print(e)
            if curr_rst_md5 == pre_rst_md5:
                break
            pre_rst_md5 = curr_rst_md5

            if  news_year and news_year< year:
                year = news_year
            index += 1
    
    print(len(data))
    return data
    

def main():
    pass

if __name__ == '__main__':
    keywords = ["Climate change", "Climate adaptation", "Environmental crisis", "Greenhouse gases","Carbon emissions", "Renewable energy","Sustainable development",
                "Extreme weather","Sea level rise","Biodiversity loss","Climate action","Paris Agreement","COP26 (or other UN climate conferences)","Climate policy",
                "Climate science","COP15","Environmental policy","Climate policy","Climate advocacy"
                ]

    data = []
    # data.extend(get_cnn(keywords))
    # df_cnn = pd.DataFrame(data)
    # df_cnn.to_csv("news_cnn.csv", index=False)

    df = pd.DataFrame(data)
    df.to_csv("abc.csv", index=False)
    # text = get_abc_body("https://abcnews.go.com/Business/wireStory/dutch-court-nixes-plan-reduce-flights-schiphol-airport-98372887")
    # print(text)
    # print(len(text.split()))