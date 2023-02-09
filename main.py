import argparse
import urllib3
import csv
import time
import mysql.connector

database_config = {
    'user': 'danielsokil',
    'password': 'password',
    'host': '127.0.0.1',
    'database': 'google_sheets',
    'raise_on_warnings': True
}

parser = argparse.ArgumentParser(
    description="Google Sheet To MySQL", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-u", "--csv-url",
                    help="Link To Google Sheet CSV URL")
args = parser.parse_args()

csv_url = args.csv_url


def fetch_csv(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return response.data.decode()


mysql_connection = mysql.connector.connect(**database_config)
mysql_cursor = mysql_connection.cursor()

try:
    mysql_cursor.execute("CREATE TABLE sheet1 (asset_id VARCHAR(255) PRIMARY KEY UNIQUE, serial_number VARCHAR(255), model_hashrate VARCHAR(255), reported_hashrate VARCHAR(255), control_board_type VARCHAR(255), psu_type VARCHAR(255), tested_at VARCHAR(255), notes VARCHAR(255))")
except:
    print("Table sheet1 Already Exists")

add_row = ("INSERT INTO sheet1 (asset_id, serial_number, model_hashrate, reported_hashrate, control_board_type, psu_type, tested_at, notes) VALUES (%(asset_id)s, %(serial_number)s, %(model_hashrate)s, %(reported_hashrate)s, %(control_board_type)s, %(psu_type)s, %(tested_at)s, %(notes)s) ON DUPLICATE KEY UPDATE serial_number=%(serial_number)s, model_hashrate=%(model_hashrate)s, reported_hashrate=%(reported_hashrate)s, control_board_type=%(control_board_type)s, psu_type=%(psu_type)s, tested_at=%(tested_at)s, notes=%(notes)s")


def update_db():
    csv_data = fetch_csv(csv_url)
    csv_reader = csv.DictReader(csv_data.splitlines())
    for row in csv_reader:
        row_data_formatted = {
            'asset_id': row["Asset ID"],
            'serial_number': row["SERIAL NUMBER"],
            'model_hashrate': row["MODEL HASHRATE"],
            'reported_hashrate': row["REPORTED HASHRATE"],
            'control_board_type': row["CONTROL BOARD TYPE"],
            'psu_type': row["PSU TYPE"],
            'tested_at': row["TESTED AT"],
            'notes': row["NOTES"]
        }

        mysql_cursor.execute(add_row, row_data_formatted)

    mysql_connection.commit()


try:
    while True:
        current_time = time.strftime("%I:%M %p")
        print(f"{current_time}: Updating Database")
        update_db()
        print(f"{current_time}: Sleeping For 10 Seconds")
        time.sleep(10)
finally:
    mysql_cursor.close()
    mysql_connection.close()
