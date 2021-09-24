from bs4 import BeautifulSoup
import os
import pandas as pd



class BaseParser():
    def __init__(self, folder):
        dfs = []
        for f in os.listdir(folder):
            timestamp = f.split('/')[-1].split('.')[0]
            try:
                with open(os.path.join(folder,f), 'r', encoding = 'utf-8') as fp:
                    soup = BeautifulSoup(fp.read(), 'html.parser')
                df = self.parse(soup)
            except Exception as e:
                print('Could not parse file: ', f)
                print(e)
                df = pd.DataFrame()
            print(df.shape, f)
            df['timestamp'] = timestamp
            dfs.append(df)
        
        self.df = pd.concat(dfs)
  
        pass


class BaseSuper(BaseParser):
    def __init__(self, *args, **kwargs):
        # Need I do this boring code? - how to replace it?
        super(BaseSuper, self).__init__(*args, **kwargs)

class BostonParser(BaseSuper):
    def parse(self,soup):
        div = soup.find('div',class_ = 'field-type-text-with-summary')
        employees = div.find_all('ul')
        employee_list = []
        for d in employees:
            dep = d.findPrevious('h2').get_text().strip()
            employee_list.append([[' '.join(i.split('-',1)[-1].split()) for i in e.get_text().strip().split('-',1)] + [dep] for e in d.find_all('li')])

        data = [e for a in employee_list for e in a]
        df = pd.DataFrame(data, columns = ['name','position','department'])

        return df




def main():
    outdir = './data/parsed'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    BostonParser('./data/raw/boston-celtics').df.to_csv('./data/parsed/boston-celtics.csv')
    # soup = BeautifulSoup('./data/raw/boston-celtics/20210905081024.html', 'html.parser')
    # print(soup)
    pass

if __name__ == '__main__':
    main()