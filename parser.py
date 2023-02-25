from bs4 import BeautifulSoup
import requests
import medicine
import re


class Parser:
    def __init__(self, url):
        self.URL = url

    def parse(self, keyword):
        req = self.URL + "/products?keyword=" + keyword
        cont = requests.get(req)
        soup = BeautifulSoup(cont.content, 'html.parser')
        table = soup.find_all('table')[0]
        names = table.find_all('a', {'data-product': True})
        prices = table.find_all("span", class_="price")
        div = soup.find('div', {'id': 'content'})
        if div.get_text() == "Товары не найдены": return []
        medicines = []
        count = 0
        for i in range(len(prices)):
            if count == 3:
                break
            # print(names[i])
            medicine = {}
            link = "http://e-apteka.md/" + re.findall(r'href="([^"]*)"', str(names[i]))[0]
            name = names[i].get_text()
            price = prices[i].get_text()
            medicine['name'] = name
            medicine["price"] = price
            medicine["link"] = link
            # print(name, link, price)
            medicines.append(medicine)
            count += 1
        return medicines




# print(Parser("http://e-apteka.md").parse("Аспирин"))
# print(Parser("http://e-apteka.md").parse("Ибупрофен"))
