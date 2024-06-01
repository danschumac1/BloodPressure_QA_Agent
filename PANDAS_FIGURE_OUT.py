"""
Created on 05/31/2024

@author: Dan Schumacher
"""
#endregion
#region # IMPORTS
# =============================================================================
# IMPORTS
# =============================================================================

import psycopg2
import pandas as pd
from sqlalchemy import create_engine

#endregion
#region # LOADING DATA
# =============================================================================
# LOADING DATA
# =============================================================================

# Database connection parameters
username = "postgres"
password = "password"
database = "Pieces_Database"
host = "localhost"
port = "5432"

# Establish connection to the database

# Create the connection string
connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create an engine using SQLAlchemy
engine = create_engine(connection_string)

vital_query = "SELECT * FROM vital"
medication_query = "SELECT * FROM medication"

# Read data into pandas DataFrames
vital_df = pd.read_sql_query(vital_query, engine)
medication_df = pd.read_sql_query(medication_query, engine)

#endregion
#region # 
# =============================================================================
# TASK 1
# =============================================================================
# PROMPT VITAL TABLE
# Did the patient have Hypertension/Hypotension given blood-pressure records from vitals?
    # HYPOtension (low blood pressure) = blood pressure reading lower than 90 mmHg top or lower than 60 mmHg for bottom.
    # HYPERtension (high blood pressure) = at above 140/90

# LOOK FOR PatientID == X
# LOOK FOR ComponentID == BloodPressure
# FOR BloodPressure_reading: -> split on / 
    # if [0] > 140 mmHg or if [1] > 90
        # Hyper tension
    # if [0] < 90 mmHg or if [1] < 60
        # HYPOtension 

#endregion
#region # TASK 2
# =============================================================================
# TASK 2
# =============================================================================
# IF HYPER/HYPOTENSION
# PROMPT THE MEDICATION TABLE
# Look at PatientID == X
# Look for Description and ProviderInstructions that indicate blood pressure medication



#endregion
#region # EXPLORE
# =============================================================================
# EXPLORE
# =============================================================================
vital_df.head(6)
medication_df.head()