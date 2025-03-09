# Exploratory Data Analysis (EDA) - Customer Loans in Finance
End-to-End EDA Process of a dataset on customers loans.

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#Installation">Installation</a></li>
    <li><a href="#Usage">Usage</a></li>
    <li><a href="#File-Structure">File Structure</a></li>
    <li><a href="#License">License</a></li>
  </ol>
</details>

## Table of Contents
- Installation
- Usage
- File Structure
- License

## Installation
Clone for local access.
```sh
https://github.com/bc319IC/exploratory-data-analysis---customer-loans-in-finance316.git
```

## Usage
Run the appropraite files in the following section regarding their descriptions.

## File Structure

### customer_loans.ipynb
Run all in customer_loans.ipynb to view the Data Extraction and End-to-End EDA Process of the loan_payments dataset. 
Skip the data extraction step as the credentials file is not supplied.

#### db_utils.py
Run db_utils.py to load the credentials from the yaml file, initialise and connect to the SQLAlchemy engine, 
extract the loan_repayments data to a database and then convert it to a csv file. Contains the the classes for transforming
the dataframe.

#### db_plotter.py
Contains the class to visualise the results of the transformations carried out.

#### db_analyse.py
Contains the class that analyses the original dataframe.

## License
This project is licensed under the terms of the MIT license. (tbd)