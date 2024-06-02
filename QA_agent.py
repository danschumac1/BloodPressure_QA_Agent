"""
Created on 05/31/2024

@author: Dan Schumacher
"""
#region # IMPORTS & SET-UP
# =============================================================================
# IMPORTS & SET-UP
# =============================================================================
# import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import openai
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

#endregion
#region # Q&A AGENT
# =============================================================================
# FUNCTIONS
# =============================================================================
def check_blood_pressure(patient_id, vital_df):
    # GRAB ROWS THAT HAVE TO DO WITH THE REQUESTED PATIENT AND BLOOD PRESSURE READINGS
    patient_vitals = vital_df[(vital_df['patientid'] == patient_id) & (vital_df['componentid'] == 'BloodPressure')]

    # ITERATE OVER THOSE GRABBED ROWS
    for _, row in patient_vitals.iterrows():

        # SPLIT BLOOD PRESSURE TO TOP AND BOTTOM NUMBERS
        systolic, diastolic = map(int, row['observationresult'].split('/'))

        # CHECK FOR HYPER TENSION
        if systolic > 140 or diastolic > 90:
            return 'Hypertension'
        
        # CHECK FOR HYPO TENSION
        elif systolic < 90 or diastolic < 60:
            return 'Hypotension'
    
    # IF NO BP READINGS ARE DANGEROUS, RETURN NORMAL
    return 'Normal'

# check_blood_pressure('p1')
    
def retreive_medication_documentation(patient_id, medication_df):
    # GRAB ALL ROWS OF MEDICATION DF FOR PATIENT
    patient_meds = medication_df[medication_df['patientid'] == patient_id]

    # IF THERE IS NO MEDICATIONS FOR THAT PATIENT, RETURN SUCH
    if patient_meds.empty:
        medication_documentation = f"No medication found for {patient_id}"

    else: # MEDICATION DOES EXIST FOR THAT PATIENT

        # MAKE AN EMPTY STRING
        medication_documentation = ''

        # FOR EACH ROW OF MEDICATION
        for _, row in patient_meds.iterrows():
            # ATTACH THE DESCRIPTION AND INSTRUCTIONS TO THE BLANK STRING
            med_row = 'DESCRIPTION: ' + row['description'].strip().lower() + ' || PROVIDER INSTRUCTIONS: ' + row['providerinstructions'].strip().lower() + '\n'
            medication_documentation += (med_row)
    
    # RETURN ALL INSTRUCTIONS AND DESCRIPTIONS IN A BIG LONG STRING
    return medication_documentation

# print(retreive_medication_documentation('p1'))

def main():
    # =============================================================================
    # API CONFIG
    # =============================================================================

    # Load environment variables from the .env file
    load_dotenv()

    # Get the API key from the environment variable
    api_key = os.getenv("OPENAI_API_KEY")

    # Check if the API key is available
    if api_key is None:
        raise ValueError("API key is missing. Make sure to set OPENAI_API_KEY in your environment.")

    # Set the API key for the OpenAI client
    openai.api_key = api_key
    client = OpenAI(api_key=api_key)

    #endregion
    #region # LOADING DATA
    # =============================================================================
    # LOADING DATA
    # =============================================================================
    # Database connection string
    database_url = os.getenv("DB_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not set in the environment variables")

    # Ensure the connection string uses the correct dialect
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Create an engine using SQLAlchemy
    engine = create_engine(database_url)

    # Create queries
    vital_query = "SELECT * FROM vital"
    medication_query = "SELECT * FROM medication"

    # Read data into pandas DataFrames
    vital_df = pd.read_sql_query(vital_query, engine)
    medication_df = pd.read_sql_query(medication_query, engine)

    # =============================================================================
    # PROMPTING
    # =============================================================================
    patient_name = input("Enter the patient name (p1 or p2): ")

    if patient_name in vital_df['patientid'].values:
        blood_pressure_status = check_blood_pressure(patient_name, vital_df)

        if blood_pressure_status != 'normal':

            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125", # keep it cheap until it is working
                messages=[

                # HIGH LEVEL WHAT WILL THE MODEL BE DOING
                { 
                    "role": "system",
                    "content": '''
        Act as a physician. Your job, specifically, is to look at medical records of patients who have been diagnosed with hypertension or hypotension to find out what sort of treatment (if any) they have received. Then return that information to the user.
        '''
                
                },

                # EXAMPLE WHERE PATIENT HAS RECEIVED TREATMENT
                # These were generated with ChatGPT 4o and reviced by a infectious disease doctor (friend of mine) 
                {
                "role": "user",
                "content": f"""
        PATIENT NAME: p0
        BLOOD PRESSURE STATUS: Hypertension
        MEDICAL RECORDS: 
        DESCRIPTION: metoprolol tartrate 25 mg tablet || PROVIDER INSTRUCTIONS: administer orally twice daily. Monitor heart rate and blood pressure regularly.
        DESCRIPTION: insulin glargine 100 units/ml injection pen || PROVIDER INSTRUCTIONS: inject subcutaneously once daily at the same time each day. Adjust dose based on blood glucose levels. 
        DESCRIPTION: furosemide 40 mg tablet || PROVIDER INSTRUCTIONS: administer orally once daily in the morning. Monitor for signs of dehydration and electrolyte imbalance.
        TREATMENT: The patient has received treatment for their hypertension with metoprolol tartrate 25 mg tablet, which is to be administered orally twice daily, with regular monitoring of heart rate and blood pressure. Additionally, furosemide although a diarrhetic, will have an effect of lowering blood pressure. It is not listed as an antihypertensive, but it will have that effect.[END]
        """
                },

                # EXAMPLE WHERE THE PATIENT HAS NOT RECEIVED TREATMENT
                # These were generated with ChatGPT 4o and reviced by a infectious disease doctor (friend of mine) 
                {
                "role": "user",
                "content": f"""
        PATIENT NAME: p4
        BLOOD PRESSURE STATUS: Hypotension
        MEDICAL RECORDS:  
        DESCRIPTION: amoxicillin 500 mg capsule || PROVIDER INSTRUCTIONS: administer orally every 8 hours. Complete the full course of the antibiotic even if symptoms improve. 
        DESCRIPTION: ondansetron 4 mg oral disintegrating tablet || PROVIDER INSTRUCTIONS: place on the tongue to dissolve; do not swallow whole. Administer 30 minutes before chemotherapy to prevent nausea and vomiting. 
        DESCRIPTION: lorazepam 1 mg tablet || PROVIDER INSTRUCTIONS: administer orally as needed for anxiety, not to exceed 3 doses per day. Monitor for signs of drowsiness or sedation. 
        TREATMENT: The patient has not received treatment specifically for hypotension. The medications listed in the medical records are for other conditions such as infection, nausea/vomiting prevention, and anxiety. Two of the medications (amoxicillin and ondansetron) do not treat hypotension, but might treat the cuases of hypotension.[END]
        """
                },
                {
                "role": "user",
                "content": f"""
        PATIENT NAME: p5
        BLOOD PRESSURE STATUS: Hypotension
        MEDICAL RECORDS:
        TREATMENT: The patient has not received any treatment specifically for hypotension. In fact they have no entries on the medication database whatsoever.[END]
        """
                },

                # THE EXAMPLE THAT WE ARE ASKING THE MODEL ABOUT
                {
                "role": "user",
                "content": f"""
        PATIENT NAME: {patient_name}
        BLOOD PRESSURE STATUS: {blood_pressure_status}
        MEDICAL RECORDS:
        {retreive_medication_documentation(patient_name, medication_df)}
        TREATMENT:
        """
                }
            ],

            # AVOID HALLUCINATIONS WITH A LOW TEMP
            temperature=0.0,

            # DON'T WANT RESPONSE BEING TOO WORDY
            max_tokens=256,
            stop=["[END]"], 
            )

            print(json.dumps({
                'patient_name': patient_name,
                'blood_pressure_status': blood_pressure_status,
                'output': response.choices[0].message.content
            }))

        else: # NO HIGH BLOOD PRESSURE
            print(json.dumps({
                'patient_name': patient_name,
                'blood_pressure_status': blood_pressure_status,
                'output': 'Patient blood pressure is normal'
                }))
    else:
        print(f"Patient {patient_name} not found in vitals record.")

if __name__ == "__main__":
    main()
    
#endregion
#region # NOTES
# =============================================================================
# NOTES
# =============================================================================
# docker build -t blood-pressure-qa-app .
# docker run --env-file .env -it blood-pressure-qa-app

#endregion
#region # FUTURE WORK
# =============================================================================
# FUTURE WORK
# =============================================================================
# Set up and .dockerignore (Don't want openAPI key or password available)
