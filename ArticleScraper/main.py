from Scraper import generic_scraper as scraper
from Scraper import text_helper as text_helper
import pandas as pd



# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def cord_19_data_keep_only_has_full_text_df(df):
    df["pmcid"] = df["pmcid"].astype(str)
    ret = df[df["pmcid"]!='nan']
    # ret['column_name'] = ret['doi'].str.replace('http://dx.doi.org/', '', regex=False)

    print(ret.info())
    ret.to_csv('debug.csv', index=False)
    return ret



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df = cord_19_data_keep_only_has_full_text_df(pd.read_csv('./Inputs/cord-19_2020-03-20/metadata.csv'))
    # scraper.download_html_files(df)
    scraper.scrape_full_text(df)

    # df = pd.read_csv('./Outputs/Data/CORD_Data.csv')
    # df_clean = text_helper.lemmatise(df)
    # scraper.summarise_full_text(df)



