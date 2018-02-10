import scrapy 
from scikit.items import ScikitItem

#to scrape the API documentation page of scikit
class ScikitSpider(scrapy.Spider):
    name = "sci-spider"
    start_urls = ['http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html']

    def parse(self, response):
    	item = ScikitItem()
        section = response.css("div.section")
        title = section.xpath("dl/dt/code/text()")
        item['libName'] = title.extract_first()
        item['funcName'] = title.extract()[-1]
        item['funcDesc'] = section.xpath("dl/dd/p/text()").extract_first()
        item['notes'] = ' '.join([txt.strip() for txt in section.xpath("//p[text()='Notes']/following-sibling::p[not(@class='rubric')]//text()").extract()])
        mtable = response.xpath('//table[@class="longtable docutils"]')
        paramTable = []
        methods = []
        if not mtable:
            #if there's no method's table, the only table on page is ParamTable
            paramTable = response.xpath('//table[@class="docutils field-list"]')
        else:
            #table preceding method's table is paramTable
            paramTable = response.xpath('//table[@class="longtable docutils"]/preceding-sibling::table[1]')
            methods = response.xpath('//dl[@class="method"]')

        if paramTable:
            for row in paramTable.xpath('tbody/tr[@class="field-odd field"] | tbody/tr[@class="field-even field"]'):
                fieldname = row.xpath("th/text()")
                if "Parameters" in fieldname.extract_first():
                    item['allFuncParams'] = row.css("td p strong::text").extract()
                    item['funcParamBody'] = row.xpath("td/descendant::text()[not(starts-with(., '\n'))]").extract()
                if "Attributes" in fieldname.extract_first():
                    item['allFuncAttributes'] = row.css("td p strong::text").extract()
                    item['funcAttrBody'] = row.xpath("td/descendant::text()[not(starts-with(., '\n'))]").extract()
                if "Returns" in fieldname.extract_first():
                    item['allReturnParams'] = row.css("td p strong::text").extract()
                    item['funcReturnBody'] = ' '.join([txt.strip() for txt in row.xpath("td/descendant::text()[not(starts-with(., '\n'))]").extract()])
        
        #loop over methods
        if mtable:
            for method in response.xpath('//dl[@class="method"]'):
                text = ""
                for element in method.xpath("dt/descendant::text()[not(parent::a)]").extract():
                    if "\n" not in element and '[source]' not in element:
                        text = text + ''.join(element)
                item['methodName'] = text
                item['methodDesc'] = ' '.join([txt.strip() for txt in method.xpath("dd/p//text()").extract()])
                innerMethodTable = method.xpath("dd/table[@class='docutils field-list']")
                if innerMethodTable:
                    for row in innerMethodTable.xpath('tbody/tr[@class="field-odd field"] | tbody/tr[@class="field-even field"]'):
                        fieldname = row.xpath("th/text()")
                        if "Parameters" in fieldname.extract_first():
                            item['methodParams'] = row.css("td p strong::text").extract()
                            item['methodParamsBody'] = ' '.join([txt.strip() for txt in row.xpath("td//text()").extract()])
                        if "Returns" in fieldname.extract_first():
                            item['methodReturns'] = row.css("td p strong::text").extract()
                            item['methodReturnsBody'] = ' '.join([txt.strip() for txt in row.xpath("td//text()").extract()])

        yield item

                   
        #paramTable = response.xpath('//table[@class="longtable docutils"]/preceding-sibling::table[1]')
        '''
        for sites that don't have method table and just have a paramTable, check if the mtable is empty, if it is then the first table on the site would be paramTable
        mtable = response.xpath('//table[@class="longtable docutils"]')
        if not mtable:
            paramTable = response.xpath('//table[@class="docutils field-list"]')
            paramTable.extract()
        '''

        '''
        ***for odd row
        orow = paramTable.xpath('tbody/tr[@class="field-odd field"]')

        ***check the value of colHead, if it's Parameters, Attributes or Returns. Assign accordingly.  
        fieldname = orow.xpath("th/text()") 

        **to extract the entire colBody:
        funcParamDesc = orow.xpath("td/descendant::text()[not(starts-with(., '\n'))]")
        
        **for just the param details (but can't associate them to the paramNames and desc):
        funcParamDetail = orow.xpath("td/blockquote/div/p/text()")

        **for just param Desc (can be associated to the paramNames, lists of same size)
        funcParamDesc = orow.xpath("td/p/text()")

        **just the param names and param Desc as separate strings in the list:
        funcParamDesc = orow.xpath("td/descendant::text()[not(starts-with(., '\n'))]")

        #Interesting result (OF USE: TO BE FIGURED OUT)
        funcParamDesc = orow.xpath("td/descendant::*[not(starts-with(text(), '\n'))]")

        ***all methods from the page
        methods = response.xpath('//dl[@class="method"]')

        ***loop over the methods one by one and extract the text 
        for elem in methods.xpath("dt/descendant::text()[not(parent::a)]").extract():
            if "\n" not in elem and '[source]' not in elem:
                text = ''.join(elem)

        ***method description 
        methodAbout = methods.xpath("dd/p//text()")

        ***Table inside method class
        innermethodtable = methods.xpath("dd/table[@class='docutils field-list']") 

        '''






