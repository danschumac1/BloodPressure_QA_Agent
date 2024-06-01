import os
import psycopg2
import pandas as pd
from datetime import datetime

# Base directory where your files are located
base_dir = os.path.expanduser("~")  # This will get the home directory
project_dir = os.path.join(base_dir, "OneDrive", "Desktop", "pieces_audition")
os.chdir(project_dir)

# LOAD AND CLEAN DATA
# LOAD VITAL DATA
vital_path = os.path.join(project_dir, 'data', 'vital.csv')
vital_data = pd.read_csv(vital_path)

# LOAD MEDICATION DATA
medication_path = os.path.join(project_dir, 'data', 'medication.csv')
medication_data = pd.read_csv(medication_path)

# SPLIT ObservationDate INTO DATE AND TIME
vital_data[['ObservationDate', 'ObservationTime']] = vital_data['ObservationDate'].str.split(' ', expand=True)

# CREATE DATABASE CONNECTION
username = "postgres"
password = "password"
database = "Pieces_Database"
host = "localhost"
port = "5432"

try:
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        dbname=database,
        user=username,
        password=password,
        host=host,
        port=port
    )

    # Create a cursor object
    cursor = conn.cursor()

    # Create the vital table with lowercase column names
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vital (
        patientid VARCHAR(255),
        componentid VARCHAR(255),
        observationdate DATE,
        observationtime TIME,
        observationresult VARCHAR(255),
        observationunits VARCHAR(255)
    )
    """)

    # Commit the transaction
    conn.commit()

    # Create the medication table with lowercase column names
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medication (
        patientid VARCHAR(255),
        medinterval VARCHAR(255),
        orderstartdate TIMESTAMP,
        description TEXT,
        amount NUMERIC,
        units VARCHAR(255),
        dosageform VARCHAR(255),
        providerinstructions TEXT
    )
    """)

    # Commit the transaction
    conn.commit()

except Exception as e:
    print(f"An error occurred during table creation: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()

try:
    conn = psycopg2.connect(
        dbname=database,
        user=username,
        password=password,
        host=host,
        port=port
    )

    # Create a cursor object
    cursor = conn.cursor()

    # ADD TO DATABASE
    for index, row in vital_data.iterrows():
        cursor.execute("""
        INSERT INTO vital (patientid, componentid, observationdate, observationtime, observationresult, observationunits)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row['PatientID'], 
            row['ComponentID'], 
            datetime.strptime(row['ObservationDate'], '%m/%d/%Y').date(), 
            row['ObservationTime'], 
            row['ObservationResult'], 
            row['ObservationUnits']
        ))

    for index, row in medication_data.iterrows():
        if pd.notnull(row['OrderStartDate']):
            order_start_date = datetime.strptime(row['OrderStartDate'], '%m/%d/%Y %H:%M')
        else:
            order_start_date = None

        cursor.execute("""
        INSERT INTO medication (patientid, medinterval, orderstartdate, description, amount, units, dosageform, providerinstructions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['PatientID'], 
            row['MedInterval'], 
            order_start_date, 
            row['Description'], 
            row['Amount'], 
            row['Units'], 
            row['DosageForm'], 
            row['ProviderInstructions']
        ))

    # Commit the transaction
    conn.commit()

except Exception as e:
    print(f"An error occurred during data insertion: {e}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()