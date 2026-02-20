from google.cloud import bigquery
from google.oauth2 import service_account

# Path to your service account JSON key file
key_path = r"C:\Users\Odeth\Downloads\bigquery-public-data-487909-de88968af3c2.json"

# Set the project ID
project_id = "bigquery-public-data-487909"

# Use the credentials to initialize the BigQuery client
credentials = service_account.Credentials.from_service_account_file(key_path)

# Initialize BigQuery client with credentials
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Now you can query BigQuery
query = """SELECT * FROM `bigquery-public-data.chicago_crime.crime` LIMIT 10000"""
query_job = client.query(query)

# Wait for the query to finish and get the results
data = query_job.result().to_dataframe()

# Save to CSV
data.to_csv("raw_crimes.csv", index=False)

print("Data saved to raw_crimes.csv")
