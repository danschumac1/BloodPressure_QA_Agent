# Blood Pressure QA App

This repository contains a Dockerized application for analyzing patient blood pressure data and determining if they have hypertension or hypotension, as well as identifying any related treatments.

## Features

- Analyzes blood pressure data from patient records.
- Determines if a patient has hypertension or hypotension.
- Identifies treatments for the diagnosed conditions using medication data.
- Utilizes OpenAI's gpt-4-1106-preview to generate treatment summaries.

## Usage

To use this application, follow these steps:

1. **Pull the Docker Image**:
   ```bash
   docker pull danschumac1/blood-pressure-qa-app:latest
