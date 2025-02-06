from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import os
import pandas as pd

def download_html_files(df):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_ga=GA1.4.1287860501.1712095345; _ga=GA1.1.1287860501.1712095345; cloudpmc-viewer-csrftoken=Yro9cp1ua8v3njZIcfySpb6yxBmPNi1S; ncbi_sid=E5FDA19E74A178B3_8622SID; books.article.report=; _ga_DP2X732JSX=GS1.1.1734765752.10.1.1734765773.0.0.0; _ga_CSLL4ZEK4L=GS1.1.1734765752.13.1.1734765773.0.0.0; ncbi_pinger=N4IgDgTgpgbg+mAFgSwCYgFwgMIA5sAiBAogAwBMA7AGzUCsAYtQCwDMpdJFpprdx2AIKtW5AHQBbOAEYQAGhABXAHYAbAPYBDVMqgAPAC6ZQ5TCADGGxajATzAWhjIoAdygR5IVmdvnPzM31zKDADZHVlTzozT3JSMzxCLipaRhZ2TjI43n4hEXEpWQVyWSxLdWtfR2c3CAxfDCCQsIiMADkAeTbiWNMsXzFlcwAjZEHVCUHkRDEAc3UYWIBOM2lcXHiFdjNcOlxPVlKQNY2DvpBd/a3vLAAzTVUAZygDgKwDCEUXrf2sA5WsNJqKR6KYFMx4oDgbhmCtwTcQKQxMxpGJNiBmG8lGotDp9EZwdEsOi6AiTiSsZcotQzCTKLTPNQjtI+CAAL5soA',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
    }
    download_directory = "./Outputs/UnstructuredData"
    length = len(df)
    i = 1
    for index, row in df.iterrows():
        article_id = row['pmcid']
        url = f"https://pmc.ncbi.nlm.scrnih.gov/articles/{article_id}/?report=classic"

        try:
            # Send GET request
            response = requests.get(url, headers=headers)

            if 200 <= response.status_code <= 299:
                file_path = os.path.join(download_directory, f"{article_id}.html")
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"{index}/{length}: Success: {article_id}: {response.status_code}")
            else:
                print(f"{index}/{length}: Failed for {article_id}: {response.status_code}")

        except Exception as e:
            print(f"Error fetching {article_id}: {e}")

        # Delay to avoid overwhelming the server
        time.sleep(1.5)  # Delay of 1.5 seconds (adjust as needed)


# Function to extract abstract and full text using Selenium
def extract_text_with_selenium(driver, file_path):
    try:
        # Load the file
        driver.get(f"file:///{file_path}")
        time.sleep(1)

        # Extract the abstract
        try:
            abstract_text_sections = []
            abstract_elements = driver.find_elements(By.CLASS_NAME, 'abstract')
            for abstract_element in abstract_elements:
                abstract_text_sections.append(abstract_element.text)
            abstract_text = ' '.join(abstract_text_sections)
        except Exception:
            abstract_text = None

        # Extract all sections with IDs like 'sec1', 'sec2', etc.
        full_text_sections = []
        try:
            sections = driver.find_elements(By.CSS_SELECTOR, "section[id^='sec']:not(.abstract), section[id^='s']:not(.abstract)")
            for section in sections:
                full_text_sections.append(section.text)
            full_text = ' '.join(full_text_sections)
        except Exception:
            full_text = None

        return abstract_text, full_text
    except Exception as e:
        # Catch problems
        print(f"Error processing file {file_path}: {e}")
        return None, None
#
import json
def scrape_full_text(df):
    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'normal'

    driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=options)
    # input_directory = "/Outputs/UnstructuredData"
    length = len(df)
    i = 1
    for index, row in df.iterrows():
        print(f"{i}/{length}")
        article_id = row['pmcid']
        file_path = f"{os.getcwd()}/Outputs/UnstructuredData/{article_id}.html"
        if os.path.exists(file_path):
            # Extract abstract and full text
            abstract_text, full_text = extract_text_with_selenium(driver, file_path)

            record = {
                "abstract": row['abstract'] if not pd.isna(row['abstract']) else abstract_text,
                "full_text": full_text
            }

            with open(f"{os.getcwd()}/Outputs/Data/FullText/{article_id}.ndjson", "a") as f:
                f.write(json.dumps(record))
            # Update DataFrame
            # if pd.isna(row['abstract']) or not row['abstract']:
                #df.at[index, 'abstract'] = abstract_text
            #df.at[index, 'full_text'] = full_text
            #df.to_csv('./Outputs/Data/FullText.csv', index=False)
        else:
            print(f"File not found: {file_path}")
        i = i + 1

    driver.quit()