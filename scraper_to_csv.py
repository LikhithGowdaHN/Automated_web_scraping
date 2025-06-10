import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

#Paths setup
download_directory = "/Users/likhith/Downloads" #change this to your download directory or can change the download location in chrome to the project directory 
project_directory = "/Users/likhith/Desktop/cpwd_scraper" #change this to your project directory
csv_output_path = os.path.join(project_directory, "newtenders.csv")
expected_filename = "TenderAwardedDetailsReport.xls"

#mapping for final CSV
csv_cols = {
    "NIT/RFP NO": "ref_no",
    "Name of Work / Subwork / Packages": "title",
    "Estimated Cost(INR)": "tender_value",
    "Bid Submission Closing Date & Time": "bid_submission_end_date",
    "EMD Amount": "emd",
    "Bid Opening Date & Time": "bid_open_date"
}

#Setup Selenium options
chrome_options = Options()
prefs = {"download.default_directory": download_directory}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(), options=chrome_options)

try:
    #Open CPWD website
    driver.get("https://etender.cpwd.gov.in/")
    print("Opened CPWD eTender website")

    #Handle alert
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Alert found: {alert.text}")
        alert.accept()
        print("Alert accepted.")
    except (NoAlertPresentException, TimeoutException):
        print("No alert present.")

    #"Tender Information" > "All Tenders"
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Tender Information"))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "All Tenders"))
    ).click()

    #"New Tenders"
    status_dropdown = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "nStatus"))
    )
    select = Select(status_dropdown)
    select.select_by_visible_text("New Tenders")
    print("Selected 'New Tenders' in dropdown.")

    #"Search"
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnSearch"))
    ).click()

    #Export Excel
    time.sleep(3) #wait for table to load
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnExportExcel"))
    ).click()
    print("Clicked on 'Export Excel'.")

    # Step 7: Wait for download to complete
    print("⏳ Waiting for Excel to download...")
    downloaded_file = None
    for _ in range(30):  # max wait ~30 sec
        file_path = os.path.join(download_directory, expected_filename)
        if os.path.exists(file_path):
            downloaded_file = file_path
            break
        time.sleep(1)

    if not downloaded_file:
        raise FileNotFoundError("Excel file not downloaded.")

    print(f"Excel downloaded: {downloaded_file}")

    #Read Excel and process
    df = pd.read_excel(downloaded_file)
    filtered_df = df[list(csv_cols.keys())].rename(columns=csv_cols).head(20)

    #Save to CSV
    os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)
    filtered_df.to_csv(csv_output_path, index=False)
    print(f"Filtered CSV saved at: {csv_output_path}")

finally:
    driver.quit()
    print("🧹 Browser closed.")