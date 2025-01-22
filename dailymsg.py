import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "samar03042000@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "oehk scmc vxwe skkh"  # Replace with your email password
RECIPIENT_EMAIL = "ksamarasimhareddy88@gmail.com"  # Replace with recipient's email

# URL of the page to scrape
url = "https://www.investorgain.com/report/live-ipo-gmp/331/"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the table in the webpage
    table = soup.find('table', {'class': 'table table-bordered table-striped table-hover w-auto'})

    # Check if the table is found
    if table:
        # Extract table headers
        headers = [header.text.strip() for header in table.find_all('th')]

        # Extract table rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = []
            for cell in row.find_all('td'):  # Loop through all <td> cells
                # Check if the cell contains an image for Fire Rating
                img_tag = cell.find('img')
                if img_tag and 'fire' in img_tag['src']:
                    # Extract the title attribute from the <img> tag, which contains the rating
                    rating = img_tag['title']
                    cells.append(rating)  # Append rating to the row
                else:
                    # Check if the cell contains a link
                    link = cell.find('a')
                    if link:
                        cells.append(link.text.strip())  # Extract text from the link
                    else:
                        cells.append(cell.text.strip())  # Extract plain text
            rows.append(cells)

        # Create a DataFrame from the extracted data
        ipo_data = pd.DataFrame(rows, columns=headers)

        # Parse and filter the data
        current_year = datetime.today().year  # Current year for date parsing
        ipo_data['Fire Rating'] = ipo_data['Fire Rating'].str.extract(r'(\d+)').astype(float)  # Extract numeric rating

        # Convert "Open" column to datetime with explicit year
        ipo_data['Open'] = ipo_data['Open'].str.strip()  # Strip any unwanted spaces
        ipo_data['Open'] = ipo_data['Open'].apply(lambda x: f"{x}-{current_year}" if x else None)
        ipo_data['Open'] = pd.to_datetime(ipo_data['Open'], errors='coerce', format='%d-%b-%Y')

        # Drop rows where "Open" or "Fire Rating" is missing
        ipo_data = ipo_data.dropna(subset=['Open', 'Fire Rating'])

        # Get today's date
        today = pd.Timestamp(datetime.today().date())

        # Filter IPOs where "Open" is today or in the future and rating >= 3
        filtered_data = ipo_data[ipo_data['Status'].str.contains(r'\b(Open|Upcoming)\b', case=False, na=False) & (ipo_data['Fire Rating'] >= 3)
]
        # Debugging: Verify filtered data
        print("Filtered Data:\n", filtered_data)

        if not filtered_data.empty:
            # Prepare the email content
            email_subject = "Filtered IPO Details"
            email_body = f"Here are the IPOs with Fire Rating >= 3 and Open dates today or in the future:\n\n"
            email_body += filtered_data.to_string(index=False)

            # Send the email
            try:
                # Set up the email
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = RECIPIENT_EMAIL
                msg['Subject'] = email_subject
                msg.attach(MIMEText(email_body, 'plain'))

                # Connect to the SMTP server and send the email
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
    else:
        print("Table not found on the webpage.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
