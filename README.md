# exploratory-data-analysis---customer-loans-in-finance316
End-to-End EDA Process of a dataset to do with customers loans.

## Table of Contents
- Installation
- Usage
- File Structure
- License Information

## Installation
clone https://github.com/bc319IC/exploratory-data-analysis---customer-loans-in-finance316.git` for local access.

## Usage
Run the appropraite files in the following section regarding their descriptions.

## File Structure

### customer_loans.ipynb
Run all in customer_loans.ipynb to view the Data Extraction, End-to-End EDA Process, and Analysis of the loan_payments dataset. 
Skip the data extraction step as the credentials file is not supplied.

#### db_utils.py
Run db_utils.py to load the credentials from the yaml file, initialise and connect to the SQLAlchemy engine, 
extract the loan_repayments data to a database and then convert it to a csv file. Contains the the classes for transforming
the dataframe.

#### db_plotter.py
Contains the class to visualise the results of the transformations carried out.

#### db_analyse.py
Contains the class that analyses the original dataframe.

## License Information
This project is licensed under the terms of the MIT license. (tbd)