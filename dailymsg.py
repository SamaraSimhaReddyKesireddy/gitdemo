import requests
from bs4 import BeautifulSoup
import pandas as pd

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
                # Check if the cell contains a link
                link = cell.find('a')
                if link:
                    cells.append(link.text.strip())  # Extract text from the link
                else:
                    cells.append(cell.text.strip())  # Extract plain text
            rows.append(cells)

        # Create a DataFrame from the extracted data
        ipo_data = pd.DataFrame(rows, columns=headers)

        # Display the DataFrame
        print(ipo_data)

        # Save to a CSV file
        ipo_data.to_csv('live_ipo_gmp.csv', index=False)
        print("Data saved to live_ipo_gmp.csv")
    else:
        print("Table not found on the webpage.")

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
