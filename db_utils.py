import yaml
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.gofplots import qqplot
from scipy import stats
from scipy.special import boxcox1p


class RDSDatabaseConnector():

    def __init__(self, creds):
        '''
        Initialiases the class attributes

        Parameters
        ----------
        creds: dictionary
            a dictionary containing the necessary credentials to initialise the SQLAlchemy engine.
        '''
        self.creds = creds

    def initialise_engine(self):
        '''
        Initialises the SQLAlechemy engine.

        Parameters
        ----------
        None

        Returns
        -------
        engine
        '''
        # Construct a database URL for SQLAlchemy
        db_url = f"{'postgresql'}://{self.creds['RDS_USER']}:{self.creds['RDS_PASSWORD']}@{self.creds['RDS_HOST']}:{self.creds['RDS_PORT']}/{self.creds['RDS_DATABASE']}"
        # Create SQLAlchemy engine
        engine = create_engine(db_url)
        return engine
    
    def extract_data_to_dataframe(self, table_name):
        '''
        Extracts data from the sql table as a dataframe.

        Parameters
        ----------
        table_name

        Returns
        -------
        df
        '''
        # Initialise SQLAlchemy engine
        engine = self.initialise_engine()
        # Read data from the specified table into a dataframe
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, engine)
        return df
   
    @staticmethod
    def save_dataframe_to_csv(df, file_path):
        '''
        Saves the dataframe as a CSV.

        Parameters
        ----------
        df, file_path

        Returns
        -------
        None
        '''
        df.to_csv(file_path, index=False)


class DataTransform():

    def __init__(self,df):
        '''
        Initialiases the class attributes

        Parameters
        ----------
        df: dataframe
            dataframe for column types to be updated.
        '''
        self.df = df

    def convert_to_datetime(self, col_name):
        '''
        Converts the column type to datetime.

        Parameters
        ----------
        col_name

        Returns
        -------
        None
        '''
        self.df[col_name] = pd.to_datetime(self.df[col_name], format='%b-%Y')
    
    def convert_to_float(self, col_name):
        '''
        Converts the column type to float.

        Parameters
        ----------
        col_name

        Returns
        -------
        None
        '''
        self.df[col_name] = pd.to_numeric(self.df[col_name], errors='coerce').astype(float)
    
    def convert_to_int(self, col_name):
        '''
        Converts the column type to integer.

        Parameters
        ----------
        col_name

        Returns
        -------
        None
        '''
        self.df[col_name] = pd.to_numeric(self.df[col_name], errors='coerce').astype(int)
    
    def convert_to_category(self, col_name):
        '''
        Converts the column type to category.

        Parameters
        ----------
        col_name

        Returns
        -------
        None
        '''
        self.df[col_name] = self.df[col_name].astype('category')

    def convert_to_bool(self, col_name):
        '''
        Converts the column type to boolean.

        Parameters
        ----------
        col_name

        Returns
        -------
        None
        '''
        self.df[col_name] = self.df[col_name].astype(bool)

    def convert_term_to_numeric(self, col_name):
        '''
        Converts the column type to numeric by extracting only the digits part of a string.

        Parameters
        ----------
        col_name

        Returns
        -------
        None
        '''
        self.df[col_name] = self.df[col_name].str.extract('(\d+)')


class DataFrameInfo():

    def __init__(self, df):
        '''
        Initialiases the class attributes

        Parameters
        ----------
        df: dataframe
            dataframe to be analysed.
        '''
        self.df = df
    
    def d_types(self):
        '''
        Finds the data type of all columns.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        print("DataFrame dtypes: \n", self.df.dtypes)
    
    def described(self):
        '''
        Describes the dataframe.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        print("DataFrame described: \n", self.df.describe())
    
    def count_distinct_vals(self):
        '''
        Counts the distinct values in the categorical columns.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        distinct_vals = {}
        for col in self.df.select_dtypes(include=['category']):
            distinct_vals[col] = self.df[col].nunique()
        print("DataFrame distinct values: \n", distinct_vals)
    
    def shape(self):
        '''
        Returns the shape of the dataframe.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        print("DataFrame shape: \n", self.df.shape)
    
    def count_null_vals(self):
        '''
        Finds the number and percentage of nulls in the dataframe.

        Parameters
        ----------
        None

        Returns
        -------
        null_counts, null_percentage
        '''
        null_counts = self.df.isnull().sum()
        null_percentage = null_counts / len(self.df) * 100
        print("DataFrame nulls: \n", null_counts, "DataFrame nulls as %: \n", null_percentage)
        return null_counts, null_percentage


class DataFrameTransform(DataFrameInfo):

    def __init__(self, df):
        '''
        Initialiases the class attributes

        Parameters
        ----------
        df: dataframe
            dataframe to be transformed.
        '''
        super().__init__(df)

    def drop_null_cols(self, threshold=50):
        '''
        Drops the null columns with more than half null entries.

        Parameters
        ----------
        threshold - 0 to 100

        Returns
        -------
        None
        '''
        null_counts, null_percentage = self.count_null_vals()
        columns_to_drop = null_percentage[null_percentage > threshold].index
        self.df.drop(columns_to_drop, axis=1, inplace=True)
    
    def impute_null_cols(self, col_name, strategy):
        '''
        Imputes the null columns with mean or median or mode.

        Parameters
        ----------
        strategy - 'mean' or 'median' or 'mode'

        Returns
        -------
        None
        '''
        # Mean
        if strategy == 'mean':
            mean_value = self.df[col_name].mean()
            self.df[col_name].fillna(mean_value, inplace=True)
        # Median
        elif strategy == 'median':
            median_value = self.df[col_name].median()
            self.df[col_name].fillna(median_value, inplace=True)
        # Mode
        elif strategy == 'mode':
            mode_value = self.df[col_name].mode()[0]
            self.df[col_name].fillna(mode_value, inplace=True)
        else:
            raise ValueError("Invalid imputation strategy. Please choose 'mean' or 'median' or 'mode'.")
        
    def identify_skewed_cols(self, excluded_cols, threshold=0.5):
        '''
        Identifies which columns have skew above the threshold and to be considered 'skewed' columns.
        Prints the column names and skewness.

        Parameters
        ----------
        excluded_cols, threshold - 0 to 1

        Returns
        -------
        skewed_cols
        '''
        # Select only numerical columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col not in excluded_cols]
        # Calculate skewness
        skewness = self.df[numeric_cols].skew()
        skewed_cols = skewness[abs(skewness) > threshold].index
        print(skewed_cols,'\n', skewness)
        return skewed_cols
    
    def transform_skewed_cols(self, col_name, transform='yeojohnson'):
        '''
        Transforms the column using the specified transform method.

        Parameters
        ----------
        col_name, transform - 'log' or 'boxcox' or 'yeojohnson'

        Returns
        -------
        None
        '''
        # Log
        if transform == 'log':
            self.df[col_name + '_log'] = self.df[col_name].map(lambda i: np.log(i) if i > 0 else 0)
        # Box-cox
        elif transform == 'boxcox':
            boxcoxed = self.df[col_name]
            boxcoxed = stats.boxcox(boxcoxed)
            self.df[col_name + '_boxcox'] = pd.Series(boxcoxed[0])
        # Yeo-Johnson
        elif transform == 'yeojohnson':
            yeojohnsoned = self.df[col_name]
            yeojohnsoned = stats.yeojohnson(yeojohnsoned)
            self.df[col_name + '_yeojohnson'] = pd.Series(yeojohnsoned[0])
        else:
            raise ValueError("Invalid transform. Please choose 'log' or 'boxcox' or 'yeojohnson'.")

    def remove_outliers(self, excluded_cols, threshold=3):
        '''
        Removes outliers from the dataframe above the z score threshold.

        Parameters
        ----------
        excluded_cols, threshold

        Returns
        -------
        None
        '''
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col not in excluded_cols]
        outlier_indices = set()
        for col in numeric_cols:
            # Calculate z-scores
            z_scores = (self.df[col] - self.df[col].mean()) / self.df[col].std()
            # Find rows with z-scores above threshold
            col_outlier_indices = z_scores[abs(z_scores) > threshold].index
            outlier_indices.update(col_outlier_indices.tolist())
        outlier_indices = list(outlier_indices)
        # Remove rows with z-scores above threshold
        self.df = self.df.drop(index=outlier_indices, axis=0, inplace=True)

    def get_highly_correlated_cols(self, excluded_cols, threshold=0.9):
        '''
        Gets the highly correlated columns.

        Parameters
        ----------
        excluded_cols, threshold - 0 to 1

        Returns
        -------
        to_drop
        '''
        # Select only numerical columns for the correlation matrix
        numerical_df = self.df.select_dtypes(include=[np.number])
        numerical_df = numerical_df.drop(columns=excluded_cols)
        # Compute the correlation matrix
        corr_matrix = numerical_df.corr().abs()
        # Select upper triangle of correlation matrix
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
        # Find index of feature columns with correlation greater than the threshold
        to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
        print(f"Columns to drop: {to_drop}")
        return to_drop

    def remove_highly_correlated_cols(self, excluded_cols, threshold=0.9):
        '''
        Removes the highly correlated columns.

        Parameters
        ----------
        excluded_cols, threshold - 0 to 1

        Returns
        -------
        None
        '''
        # Drop the columns returned from get_highly_correlated_cols
        to_drop = self.get_highly_correlated_cols(excluded_cols, threshold)
        self.df.drop(columns=to_drop, inplace=True)
        print(f"Removed columns: {to_drop}")


def load_creds():
    '''
        Saves the credentials from a yaml file as a dictionary.

        Parameters
        ----------
        None

        Returns
        -------
        creds
        '''
    file_path = "credentials.yaml"
    try:
        with open(file_path, 'r') as file:
            creds = yaml.safe_load(file)
        return creds
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error loading YAML file: {e}")
        return None
    
def load_data_to_dataframe(file_path):
    '''
        Loads data from a CSV file into a dataframe.

        Parameters
        ----------
        file_path

        Returns
        -------
        df
        '''
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error loading data to DataFrame: {e}")
        return None
    

if __name__ == '__main__':
    #Save the CVS file from RDS Database
    creds = load_creds()
    rds = RDSDatabaseConnector(creds)
    engine = rds.initialise_engine()
    df_temp = rds.extract_data_to_dataframe('loan_payments')
    rds.save_dataframe_to_csv(df_temp, 'loan_payments.csv')
