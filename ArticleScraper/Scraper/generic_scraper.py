from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from random import randrange
import time
import os
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        url = f"https://pmc.ncbi.nlm.nih.gov/articles/{article_id}/?report=classic"

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
        # Load the HTML file in the browser
        driver.get(f"file:///{file_path}")
        time.sleep(1)  # Allow time for the page to load

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
        print(f"Error processing file {file_path}: {e}")
        return None, None
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
#
# import transformer
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import pipeline
# from gensim.summarization import summarize

def call_gpt_2(document_text):
    """ Code adapted from https://www.linkedin.com/pulse/how-develop-gpt-2-based-application-dhiraj-patra/ """
    """ Prompt from https://community.openai.com/t/prompt-engineering-for-rag/621495/2"""

    # xi haga hekk irridu naghmlu
    # summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    # summarized = summarize(document_text, word_count=990, do_sample=False)
    # TODO: further work in summarizer
    prompt = f"""DOCUMENT:
                {document_text}
                
                QUESTION: How can the above unstructured scientific article be summarized to serve as input for a 
                scientific RAG-based application, focusing on key findings and results, while considering 
                pre-processing, dense and sparse retrieval mechanisms, and query augmentation strategies? 
                
                INSTRUCTIONS:
                    Answer the users QUESTION using the DOCUMENT text above
                    Keep your answer ground in the facts of the DOCUMENT
                    If the DOCUMENT doesn’t contain the facts to answer the QUESTION return NONE else summarise""".format(
        doc=document_text)

    # Load the GPT-2 model
    # Params here https://huggingface.co/docs/transformers/en/model_doc/gpt2
    model_name = "gpt2"
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    # tokenize the prompt
    input_ids = tokenizer.encode(prompt, add_special_tokens=True, return_tensors="pt")
    # if input_ids.shape[1] > 1024:
    #     print('truncated')
    #     input_ids = input_ids[:, :1024]  # Truncate to max tokens

    # generate the summaries
    output = model.generate(
        input_ids,
        attention_mask=input_ids,
        pad_token_id=tokenizer.eos_token_id,
        max_length=1024,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        temperature=0.7,
        top_k=50,
        top_p=0.95
    )

    summary = tokenizer.decode(output[0], skip_special_tokens=True)
    print(summary)
    print()

    return summary

def summarise_full_text(df):
    print(df.info())
    for index, row in df.head(5).iterrows():
        # print(row['full_text'])
        if pd.isna(row['full_text']):
            print(f'No data at {index}')
        else:
            df['summary'] = call_gpt_2(row['full_text'])
    df.to_csv('./Outputs/Data/CORD_Data_With_Summary_POC.csv', index=False)

# Define relevant headers
relevant_headers = [
    "abstract", "title", "introduction", "discussion", "results",
    "methods", "materials", "methods", "conclusion", "summary",
    "keywords", "figures", "tables", "analysis", "comparison"
]

# Normalize text for comparison
def is_relevant_header(header_text):
    return any(keyword in header_text.lower() for keyword in relevant_headers)


def beautiful_soup_scrape():
    page_to_scrape = requests.get("http://quotes.toscrape.com")
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")

    quotes = soup.findAll("span", attrs={"class": "text"})

    for quote in quotes:
        print(quote.text)

def fetch_relevant_columns(row, driver):
    """
    Iterate in page, locate data, take inner text inside of section
    :return:
    """

    # Find all sections and headers
    extracted_data = {}
    for section in driver.find_all(['section', 'div', 'h1', 'h2', 'h3', 'h4', 'h5']):
        # Look for headers within the section
        header = section.find(['h1', 'h2', 'h3', 'h4', 'h5'])
        if header and is_relevant_header(header.text):
            # Extract text under the relevant section
            section_title = header.text.strip()
            section_content = section.get_text(separator="\n", strip=True)
            extracted_data[section_title] = section_content

def fetch_html_pages_with_selenium(url, page_limit=10):
        """
        Use Selenium to navigate and retrieve multiple pages of HTML content.
        """
        # Initialize Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'normal'

        driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=options)

        # driver = webdriver.Chrome()  # Adjust for your preferred browser (e.g., Edge, Firefox)
        driver.get(url)

        html_pages = []
        wait = WebDriverWait(driver, 20)

        try:
            for i in range(page_limit):
                print(f"Fetching page {i + 1}...")

                # Wait until the <article> tag is loaded
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))

                # Get the HTML content of the page
                # html_content = driver.page_source
                #
                # extracted_data, headers_found = extract_sections_with_bs4(html_content)
                # if not headers_found:
                #     print("No relevant headers found. Skipping this page.")
                # else:
                #     print("Relevant headers found. Adding page to the list.")
                #     html_pages.append(html_content)
                # html_pages.append(html_content)
                # fetch_relevant_columns(row, webdriver)

                # find element in a page .. element must contain text thaat I want, and be located in a header(if problem header must be either h1 or h2). If found, take the section and place
                extracted_data = {}
                all_sections = driver.find_elements(By.XPATH, )
                for section in all_sections:  # Look for headers within the section
                    header = section.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                    if header and is_relevant_header(header.text):
                        # Extract text under the relevant section
                        section_title = header.text.strip()
                        section_content = section.get_text(separator="\n", strip=True)
                        extracted_data[section_title] = section_content

                # Introduce a delay between navigations
                delay = randrange(2, 5)
                print(f"Delaying for {delay:.2f} seconds...")
                time.sleep(delay)

                # Attempt to go to the next page if applicable
                try:
                    next_button = driver.find_element(By.LINK_TEXT, "Next")
                    next_button.click()
                except:
                    print("No more pages to navigate.")
                    break
        finally:
            driver.quit()

        return html_pages


def scrape_data(df):
    # options.add_experimental_option('prefs', {
    #     "download.default_directory": "../Inputs/Outputs/PDF_To_HTML/PDF",
    #     "download.prompt_for_download": False, # automatically download
    #     "download.directory_upgrade": True,
    #     "plugins.always_open_pdf_externally": True
    # })
    for index, row in df.head(5).iterrows():
        url = f"https://pmc.ncbi.nlm.nih.gov/articles/{row['pmcid']}/?report=classic"
        # prepare preparatory file to scrape data from
        # export urls to scrape in notepad that constantly updates with progress
        # Example: Simulate multiple HTML pages (replace with actual HTML content)

        html_pages = fetch_html_pages_with_selenium(url)
        if len(html_pages) <= 0:
            print(f'skipped as did not find {row["pmcid"]}')
            continue


        # Scrape with respectful delays
        extracted_data = respectful_scrape(html_pages)

        # Convert data to DataFrame
        df = pd.DataFrame(extracted_data)
    # for
# Process the pages with BeautifulSoup
        all_data = []
        for html_content in html_pages:
            data = extract_sections_with_bs4(html_content)
            if data:
                all_data.append(data)

        # Convert to DataFrame and save
        df = pd.DataFrame(all_data)
        print(df)
        df.to_csv("scraped_articles.csv", index=False)
    # wait until page loads (aka we see article tag- wait max 7 seconds, if we don't manage, we skip)


        # time.sleep(randrange(6 , 11))
        # pdf_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        # # if has elements
        # time.sleep(10)
        #
        # # Print and handle each PDF link
        # for pdf in pdf_elements:
        #     pdf_url = pdf.get_attribute('href')
        #     print(f"PDF found: {pdf_url}")
        #
        #
        # time.sleep(10)


    # driver.quit()


def extract_sections_with_bs4(html_content):
    """
    Extract relevant sections from HTML content using BeautifulSoup.
    """
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')


    # Extract the <article> content
    article = soup.find("article", lang="en")
    if not article:
        print("No article found")
        return None

    # Find all sections and headers
    extracted_data = {}
    for section in article.find_all(['section', 'div', 'h1', 'h2', 'h3', 'h4', 'h5']):
        # Look for headers within the section
        header = section.find(['h1', 'h2', 'h3', 'h4', 'h5'])
        if header and is_relevant_header(header.text):
            # Extract text under the relevant section
            section_title = header.text.strip()
            section_content = section.get_text(separator="\n", strip=True)
            extracted_data[section_title] = section_content

    return extracted_data


def respectful_scrape(html_pages):
    """
    Scrape a batch of HTML pages with delays to avoid overburdening servers.
    """
    all_data = []
    for idx, html_content in enumerate(html_pages):
        print(f"Processing page {idx + 1}...")

        # Extract data using BeautifulSoup
        data = extract_sections_with_bs4(html_content)
        if data:
            all_data.append(data)

        # Introduce a random delay between 2-5 seconds
        delay = randrange(2, 5)
        print(f"Delaying for {delay:.2f} seconds...")
        time.sleep(delay)

    return all_data

