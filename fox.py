import requests
import pandas as pd
from lxml import etree
from datetime import datetime
from hashlib import md5
import json
import time

headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
}
def get_fox_body(url):
    """get fox info"""

    text = []
    # requests.packages.urllib3.disable_warnings()
    try:
        res = requests.get(url, headers=headers, verify=False)
        html = etree.HTML(res.text)
        x = html.xpath('//*[@id="wrapper"]/div[3]/div[1]/main/article/div/div[1]/div/p')
        for p in x:
            text.extend(p.xpath('./text()'))
    except Exception:
        pass
    
    return "\n".join(text)

def encrypt_md5(str_josn):
    # create m5 object
    new_md5 = md5()
    # have to use .encode() or it will show TypeError: TypeError: Unicode-objects must be encoded before hashing
    new_md5.update(str_josn.encode(encoding='utf-8'))
    # encrypt
    return new_md5.hexdigest() 

def get_fox(keywords):
    data = []
    url_set = set()
    for keyword in keywords:
        for i in range(2005,2023):
            date_list = [(str(i)+"0101", str(i)+"0601"), (str(i)+"0601", str(i)+"1231")]
            for d in date_list:
                index = 1
                while index < 99:
                    try:
                        url = f"https://api.foxnews.com/search/web?q={keyword}+-filetype:amp+-filetype:xml+more:pagemap:metatags-prism.section+more:pagemap:metatags-pagetype:article+more:pagemap:metatags-dc.type:Text.Article&siteSearch=foxnews.com&siteSearchFilter=i&sort=date:r:{d[0]}:{d[1]}&start={index}"
                        # requests.packages.urllib3.disable_warnings()
                        
                        res = requests.get(url,  headers=headers,verify=False)
                        rst = res.json()
                        if "items" not in rst:
                            break
                        for item in rst["items"]:
                            if "pagemap" in item and "metatags" in item["pagemap"] and len(item["pagemap"]["metatags"]) > 0:
                                meta = item["pagemap"]["metatags"][0]
                                news_url = meta["og:url"]
                                if news_url in url_set:
                                    continue

                                url_set.add(news_url)
                                time.sleep(1)
                                body = get_fox_body(news_url)
                                if len(body) == 0:
                                    continue
                                data.append({
                                    "keyword":keyword,              #keywords    
                                    "url":news_url,              #link
                                    "from" : 'fox',
                                    "headline": meta["og:title"],   #title
                                    "body": body,       #context
                                    "body_word_count" : len(body.split()),   #add word count (of the news article)
                                    "date" : meta["dc.date"]                  #publish date
                                })
                        index += 10
                    except:
                        time.sleep(1)
                        pass
    

    return data

if __name__ == "__main__":
    keywords = ["Climate change", "Climate adaptation", "Environmental crisis", "Greenhouse gases","Carbon emissions", "Renewable energy","Sustainable development",
                "Extreme weather","Sea level rise","Biodiversity loss","Climate action","Paris Agreement","COP26 (or other UN climate conferences)","Climate policy",
                "Climate science","COP15","Environmental policy","Climate policy","Climate advocacy"
                ]
    
    data = get_fox(keywords)
    df = pd.DataFrame(data)
    df.to_csv("fox.csv", index=False)