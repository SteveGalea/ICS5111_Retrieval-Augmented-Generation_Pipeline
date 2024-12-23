from Scraper import generic_scraper as scraper
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


def run_scraper_PMC():
    # Use a breakpoint in the code line below to debug your script.
    print('Running scraper')  # Press Ctrl+F8 to toggle the breakpoint.
    df = cord_19_data_keep_only_has_full_text_df(pd.read_csv('./Inputs/cord-19_2020-03-20/metadata.csv'))
    scraper.scrape_data(df)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # run_scraper_PMC()
    df = cord_19_data_keep_only_has_full_text_df(pd.read_csv('./Inputs/cord-19_2020-03-20/metadata.csv'))
    scraper.download_html_files(df)



