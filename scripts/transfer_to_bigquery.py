from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client()

table_id = "fxbg-crime-app.crime_reports.reports"

# Set the encryption key to use for the destination.
# TODO: Replace this key with a key you have created in KMS.
# kms_key_name = "projects/{}/locations/{}/keyRings/{}/cryptoKeys/{}".format(
#     "cloud-samples-tests", "us", "test", "test"
# )
job_config = bigquery.LoadJobConfig(
    autodetect=True,
    skip_leading_rows=1,
    # The source format defaults to CSV, so the line below is optional.
    source_format=bigquery.SourceFormat.CSV,
)
uri = "../data/csv_reports/crime_report_2022-11-28.csv"
load_job = client.load_table_from_uri(
    uri, table_id, job_config=job_config
)  # Make an API request.
load_job.result()  # Waits for the job to complete.
destination_table = client.get_table(table_id)
print("Loaded {} rows.".format(destination_table.num_rows))