from bs4 import BeautifulSoup
import os
import pandas as pd
from pprint import pprint



class BaseParser():
    '''
    Base parser class that sets up inputs, intermediate results and outputs.
    '''
    def __init__(self, folder=None):
        # given a folder of html files parse the staff html table from each file
        dfs = []
        if folder:
            for f in os.listdir(folder):
                # get file timestmp
                timestamp = f.split('/')[-1].split('.')[0]
                try: # try to open and parse
                    soup = self.read_html(os.path.join(folder,f))
                    # with open(os.path.join(folder,f), 'r', encoding = 'utf-8') as fp:
                    #     self.soup = BeautifulSoup(fp.read(), 'html.parser')
                    df = self.parse(soup)
                except Exception as e:
                    # if error return empty dataframe
                    print('Could not parse file: ', f)
                    print(e)
                    df = pd.DataFrame()
                print(df.shape, f)
                df['timestamp'] = timestamp
                df['date'] = pd.to_datetime(timestamp[:8], format='%Y%m%d', errors='ignore')
                dfs.append(df)
            
            self.df = pd.concat(dfs)
  
        pass

    def parse(self, soup):
        '''
        Parse staff html page into pandas dataframe with name, position, department, timestamp columns.
        '''
        pass

    def read_html(self, path):
        '''
        Read in html file using Beautiful soup and utf-8 encoding.
        '''
        with open(path, 'r', encoding = 'utf-8') as fp:
            soup = BeautifulSoup(fp.read(), 'html.parser')
        return soup

    def to_csv(self,output_path):
        '''
        Save parsed html as one csv.
        '''
        self.df.to_csv(output_path, index = False)


class BaseSuper(BaseParser):
    '''
    Super parser classes to extend base classes parameters to child classes.
    '''
    def __init__(self, *args, **kwargs):
        # Need I do this boring code? - how to replace it?
        super(BaseSuper, self).__init__(*args, **kwargs)

'''
Team specific parsers where you need to only define parse function.
'''
class BostonParser(BaseSuper):
    def parse(self,soup):

        div = soup.find('div',class_ = 'field-type-text-with-summary')
        employees = div.find_all('ul')
        employee_list = []
        for d in employees:
            dep = d.findPrevious('h2').get_text().strip()
            employee_list.append([[' '.join(i.split('-',1)[-1].split()) for i in e.get_text().replace('–','-').strip().split('-',1)] + [dep] for e in d.find_all('li')])

        data = [e for a in employee_list for e in a]
        df = pd.DataFrame(data, columns = ['name','position','department'])

        return df

class BrooklynParser(BaseSuper):
    def parse(self,soup):

        div = soup.find('div',class_ = 'boxton-container')
        employees = div.find_all('td')
        employee_list = []
        for d in employees:
            if d.has_attr('align') and d['align'] == 'right':
                dep = d.findPrevious('td',{'class':'tierone'}).get_text().strip()
                name = d.get_text().strip()
                position = d.findPrevious('td').get_text().strip()
                employee_list.append([name, position, dep])
        # pprint(employee_list)
        exclude = ['Telephone:','Fax:','Web Address:','Office Address:']
        data = [e for e in employee_list if e[1] not in exclude]
        df = pd.DataFrame(data, columns = ['name','position','department'])

        return df



def main():
    # creat parsed if it does not exist
    outdir = './data/parsed'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # parse teams
    BostonParser('./data/raw/boston-celtics').to_csv('./data/parsed/boston-celtics.csv')
    BrooklynParser('./data/raw/brooklyn-nets').to_csv('./data/parsed/brooklyn-nets.csv')
    
    pass
    

if __name__ == '__main__':
    main()