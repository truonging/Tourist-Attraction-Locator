import requests
from bs4 import BeautifulSoup

headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

url = "https://www.tripadvisor.com/Attractions-g53449-Activities-a_allAttractions.true-Pittsburgh_Pennsylvania.html"
req = requests.get(url,headers=headers,timeout=5,verify=False)
print(req.status_code)

soup = BeautifulSoup(req.content, 'html.parser')

#for x in soup.body.find_all(class_="XllAv H4 _a"):
 #   print("")
  #  print(x.text)

for x in soup.body.find_all(class_="bUshh o csemS"):
    print("")
    print(x.text)
