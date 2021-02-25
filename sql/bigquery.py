# -- queries on bigquery to export data in BQ
# -- queries in ytkojo to remove rows
#
# -- export all 2020 data to BQ
# -- videos, pipeline,
#
# -- topic
# SELECT * FROM EXTERNAL_QUERY("ytagora.US.sql2bq01", "SELECT * from topic order by id desc limit 10;");

# from oauth2client.client import GoogleCredentials
# credentials = GoogleCredentials.get_application_default()


from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client()

# TODO(developer): Set table_id to the ID of the destination table.
table_id = 'ytagora.bqytkojo.topic'
dataset_id = 'ytagora.bqytkojo'

job_config = bigquery.QueryJobConfig(destination=table_id)

job_config = bigquery.LoadJobConfig(
        write_disposition = bigquery.job.WriteDisposition.WRITE_APPEND
    )

sql = '''
    SELECT * FROM EXTERNAL_QUERY("ytagora.US.sql2bq01", "SELECT * from topic order by id asc limit 10;");
'''

# Start the query, passing in the extra configuration.
query_job = client.query(sql, job_config=job_config)  # Make an API request.
query_job.result()  # Wait for the job to complete.

print("Query results loaded to the table {}".format(table_id))

tables = client.list_tables(dataset_id)  # Make an API request.

print("Tables contained in '{}':".format(dataset_id))
for table in tables:
    print("{}.{}.{}".format(table.project, table.dataset_id, table.table_id))



# ---
