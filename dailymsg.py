from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "samar03042000@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "oehk scmc vxwe skkh"  # Replace with your email password
RECIPIENT_EMAIL = "ksamarasimhareddy88@gmail.com"  # Replace with recipient's email

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# URL of the page to scrape
url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
driver.get(url)

# Wait for the table to load
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "report_table"))
    )
    time.sleep(2)  # Small delay for rendering
except:
    print("Table not loaded in time.")
    driver.quit()
    exit()

# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Locate the table
table = soup.find('table', {'id': 'report_table'})

# Check if table is found
if not table:
    print("Table not found on the webpage.")
    exit()

# Extract table headers
headers = [header.text.strip() for header in table.find_all('th')]

# Extract table rows
rows = []
for row in table.find_all('tr')[1:]:  # Skip header row
    cells = [cell.text.strip() for cell in row.find_all('td')]
    if cells:
        rows.append(cells)

# Create a DataFrame
ipo_data = pd.DataFrame(rows, columns=headers)

# Clean and filter data
current_year = datetime.today().year
ipo_data['Open'] = ipo_data['Open'].str.strip()  # Strip spaces
ipo_data['Open'] = ipo_data['Open'].apply(lambda x: f"{x}-{current_year}" if x else None)
ipo_data['Open'] = pd.to_datetime(ipo_data['Open'], errors='coerce', format='%d-%b-%Y')

# Drop rows where "Open" is missing
ipo_data = ipo_data.dropna(subset=['Open'])

# Filter for IPOs with a 3-star rating (🔥🔥🔥)
ipo_data = ipo_data[ipo_data['Fire Rating'].str.count("🔥") == 3]

# Get today's date
today = pd.Timestamp(datetime.today().date())

# Filter IPOs where "Open" is today or in the future
filtered_data = ipo_data[ipo_data['Status'].str.contains(r'\b(Open|Upcoming)\b', case=False, na=False)]

# Debugging: Verify filtered data
print("Filtered Data:\n", filtered_data)

if not filtered_data.empty:
    # Prepare the email content
    email_subject = "IPO Details (🔥🔥🔥 Rated)"
    email_body = f"Here are the IPOs with Open dates today or in the future and 3-star rating:\n\n"
    email_body += filtered_data.to_string(index=False)

    # Send the email
    try:
        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = email_subject
        msg.attach(MIMEText(email_body, 'plain'))

        # Connect to SMTP and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
else:
    print("No IPOs match the criteria.")
