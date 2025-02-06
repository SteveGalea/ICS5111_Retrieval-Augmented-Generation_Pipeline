# Request Access To https://drive.google.com/drive/folders/1BGUcHRet3ms9LevwZaayNC8o9gO-5Zzi to access the Dataset, or choose your own fullText from this repository (we used data between 4000 -> 70000 bytes) or upload all Scraped FullText at ~\ICS5111_Retrieval-Augmented-Generation_Pipeline\ArticleScraper\Outputs\Data\FullText
# 1-mining-5-findings-Zephyr.ipynb needs to be on Kaggle/Colab, with access to GPU accelerator 
    - (make sure to "Turn On Internet" in case you use Kaggle & Activate the account + import a new dataset (upload FullText.zip) / in case of Colab, upload FullText and mount drive) 
    - Assumes it has access to FullText folder
    - Each Zephyr summarization takes 1-3 min to execute if you have between 4000 -> 70000 bytes sized fullText file
    - Generates Findings folder eventually (We made use of batches)
# 2_pre_processing_findings.ipynb - again needs to be on Kaggle/Colab, with access to GPU accelerator (same instructions as above)
    - Assumes it has access
    - Generates 4 important files in pickled folder.
# 3_Full Flow RAGs.ipynb - again needs to be on Kaggle/Colab, with access to GPU accelerator (same instructions as above)
    - Assumes access to 4 important files in pickled folder.
    - EVALUATION PROMPTS GENERATED FROM Zephyr 7B Beta compatible prompts + each prompt manually fed into GPT https://chatgpt.com/share/67a370e3-996c-800b-b619-ed9e17a68828 

# Process flows can be seen in these diagrams:
![alt text](ICS5111\ Diagram\ 1.png)
![alt text](ICS5111\ Diagram\ 2.png)
![alt text](ICS5111\ Diagram\ 3.png)