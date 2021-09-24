import pandas as pd
from waybackpy import Cdx, snapshot
import urllib.request
from requests_html import HTMLSession
import os

def get_snapshots(url, user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0", ):
    '''
    List availaible snapshots for a given url from wayback machine CDX server.
    '''

    cdx = Cdx(url=url, user_agent=user_agent)
    snapshots = cdx.snapshots()

    def snapshot_parser(snapshots):
        """
        Collect cdx snapshots into a dataframe
        """

        snaps = []
        for i, snapshot in  enumerate(snapshots, start = 1):
            snaps.append(
                (snapshot.urlkey,
                snapshot.timestamp,
                snapshot.original,
                snapshot.mimetype,
                snapshot.statuscode,
                snapshot.digest,
                snapshot.length,
                snapshot.archive_url,
                snapshot.datetime_timestamp)
            )
        columns = ("urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length","archive_url","datetime_timestamp") 
        df = pd.DataFrame(snaps,columns = columns)
        return df

    df = snapshot_parser(snapshots)

    # dedupe by year and month to get one snapshot for all available months
    df['year'] = df.datetime_timestamp.dt.year
    df['month'] = df.datetime_timestamp.dt.month
    df = df.drop_duplicates(['year', 'month'], keep = 'last')

    return df


def save_page_source(url, filename):
    '''
    Save html page source for a given url
    '''
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        session = HTMLSession()
        r = session.get(url)
        r.html.render(timeout=0, sleep=0) # makes sure the page renders Javascript
        page_content = r.html.html

        with open(filename, 'w', encoding='utf-8') as fid:
            fid.write(page_content)

    except Exception as e:
        print('\nCould not save: ')
        print(url)
        print(e, '\n')
        pass


def save_snapshots(snapshot_df, folder):
    '''
    Save page source for snapshots in the dataframe 
    '''
    for i, r in snapshot_df.iterrows():
        filename = folder + '/{}.html'.format(r.timestamp)
        print(filename)
        if not os.path.isfile(filename):
            save_page_source(r.archive_url, filename)

def main():

    # save_page_source('https://web.archive.org/web/20210630080419/https://www.nba.com/celtics/contact/front-office','data/test.html')

    # save snapshots for each team
    teams = pd.read_csv('team-links.csv')
    # keep teams with staff directory links
    teams = teams[teams.staff_directory_link != 'none']
    print(teams.head())


    for i,r  in teams.iterrows():
        print(r.prefix_2)
        snapshots = get_snapshots(r.staff_directory_link)
        folder = 'data/raw/{}'.format(r.prefix_2)
        save_snapshots(snapshots,folder)
        

if __name__ == '__main__':
    main()