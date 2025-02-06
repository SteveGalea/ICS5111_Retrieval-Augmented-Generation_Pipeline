from Scraper import generic_scraper as scraper
import pandas as pd


def cord_19_data_keep_only_has_full_text_df(df):
    df["pmcid"] = df["pmcid"].astype(str)
    ret = df[df["pmcid"]!='nan']
    # ret['column_name'] = ret['doi'].str.replace('http://dx.doi.org/', '', regex=False)

    print(ret.info())
    ret.to_csv('debug.csv', index=False)
    return ret


if __name__ == '__main__':
    # pass 1 - extract data necessary
    df = cord_19_data_keep_only_has_full_text_df(pd.read_csv('./Inputs/cord-19_2020-03-20/metadata.csv')).head(1)
    # pass 2a - download snapshot
    scraper.download_html_files(df)
    # pass 2b - scrape full_text from saved snapshots
    scraper.scrape_full_text(df)




