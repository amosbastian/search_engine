import json, os, glob, create_wordcloud
from elasticsearch import Elasticsearch, helpers
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

if __name__ == '__main__':
    for infile in glob.glob(os.path.join("XML", "*.xml")):
        print infile
        all_articles = []
        filename = os.path.splitext(os.path.basename(infile))[0]
        tree = ET.iterparse(infile)
        for _, element in tree:
            if element.tag == "{http://www.politicalmashup.nl}root":
                new_article = {
                    "date": element[1][0].text,
                    "subject": element[1][1].text,
                    "title": element[2][0].text,
                    "text": " ".join([child.text for child in element[2][1] if child.text is not None]),
                    "id": element[2].attrib["{http://www.politicalmashup.nl}id"],
                    "source": element[2].attrib["{http://www.politicalmashup.nl}source"]
                }
                create_wordcloud.create_cloud(new_article["text"], "".join(new_article["id"].split(":")))
                all_articles.append(new_article)
                element.clear()

        with open("JSON/{}.json".format(filename), "w") as f:
                    json.dump(all_articles, f, indent=4)
                
# if __name__ == '__main__':
#     for infile in glob.glob(os.path.join("XML", "*.xml")):
#         print infile
#         all_articles = []
#         filename = os.path.splitext(os.path.basename(infile))[0]
#         soup = BeautifulSoup(open(infile, "r"), "xml")

#         for article in soup.find_all("root"):
#             title = article.content.title.string
#             if title == None:
#                 body = article.content.text
#             else:
#                 title = title
#                 body = article.content.text[len(title):]
#             new_article = {
#                 "date": article.date.string,
#                 "subject": article.subject.string,
#                 "title": title,
#                 "body": body,
#                 "source": article.content["pm:source"]
#             }

#             all_articles.append(new_article)

#         with open("JSON{}.json".format(filename), "w") as f:
#                 json.dump(all_articles, f, indent=4)