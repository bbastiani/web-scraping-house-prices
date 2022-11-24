import scrapy
from datetime import datetime
import re

class AthuarSpider(scrapy.Spider):
    name = "spyder1"
    allowed_domains = ['']
    start_urls = [
        ''
    ]

    def parse(self, response):
        house_page_links = response.css('div.div-block-update1 a::attr(href)')
        yield from response.follow_all(house_page_links, self.parse_houses)

        pagination_links = response.css('div.div-block-40 a::attr(href)')
        yield from response.follow_all(pagination_links, self.parse)


    def parse_houses(self, response):
        specs = response.xpath('/html/body/div[3]/div[1]/div[2]/div/div[3]/div[3]//text()').getall()
        specs = ''.join(specs)
        specs = self.parse_house_specs(specs)
        title = response.xpath('//*[@id="detalhes"]/h1/text()').get()
        yield {
            'title': title,
            'description': response.xpath('/html/body/div[3]/div[1]/div[2]/div/div[3]/div[2]/div/text()').get(),
			'price': response.xpath('/html/body/div[3]/div[1]/div[1]/div/div[2]/span/text()').get(),
			'suites': specs['suites'],
			'rooms': specs['rooms'],
			'garage': specs['garage'],
			'bathrooms': specs['bathrooms'],
			'area': specs['area'],
			'date': datetime.now().strftime("%Y-%m-%d"),
			'address': response.xpath('/html/body/div[3]/div[1]/div[2]/div/div[3]/div[1]/div[1]/text()').get(),
            'url': response.url,
            'type': self.get_type(title)
        }

    def parse_house_specs(self, specs):
        specs_dict = dict()
        specs = specs.replace('\n','').replace('\r','').replace(' ', '')
        # result string
        # '2Banheiro(s)2Quarto(s)SimChurrasqueiraSimMuradoSimPortãoSimGradeSimSalãodefesta(s)31,00(m²)ÁreaTotal31,00(m²)ÁreaConstruída31,00(m²)ÁreaÚtil31,00(m²)ÁreaPrivativa'
        # select first character before name
        specs_dict['bathrooms'] = self.find_1_character(specs, 'Banheiro')
        specs_dict['rooms'] = self.find_1_character(specs, 'Quarto')
        specs_dict['garage'] = self.find_1_character(specs, 'Garagem')
        specs_dict['area'] = self.find_only_number(specs, ['(m²)ÁreaÚtil', '(m²)ÁreaPrivativa', '(m²)ÁreaTotal'])
        # specs_dict['address'] = self.find_1_character('Banheiro')
        specs_dict['suites'] = self.find_1_character(specs, 'Suíte')

        return specs_dict

    def find_1_character(self, specs, substr):
        idx = specs.find(substr)
        if idx < 1: return '0'
        return specs[idx-1]

    def find_only_number(self, specs, substrs, window=6):
        for substr in substrs:
            idx = specs.find(substr)
            if idx >= 0: 
                break
        if idx < 1: return '0'
        try:
            return self.getNumbers(specs[idx-window:idx])
        except Exception as e:
            self.logger.warning(e)
            return '0'

    def getNumbers(self, str):
        array = re.findall("([0-9]+[,.]+[0-9]+)", str)
        return array[0]

    def get_type(self, title):
        types = ['APARTAMENTO', 'SOBRADO', 'TERRENO', 'COBERTURA', 'CASA']
        for t in types:
            if title.find(t) >= 0:
                return t.lower()

        return ''