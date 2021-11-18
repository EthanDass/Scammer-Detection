# MutualScammerCapstone

This repo contains all the code and data we used throughout the capstone project. This readme is an attempt to help you understand the spaghetti we have cooked up :)

## Folders

### API
Let's look at the folders first. The `api` folder contains the code and files needed to run a scammer detection api. `api/schema.py` contains a [cerberus](https://docs.python-cerberus.org/en/stable/) schema of what data is expected. We tried to make your life easier and handled all the preprocessing inside the api so you should be able to pull raw data from the database for a user with the needed columns and submit it to the api.

**Except For**

The exception to this is the `analyze_data` column in the photo database. In the data we received, this column was a stringified json. The api expects to receive this as an object, not a string.

`api/model.py` is a simple class that loads a scikit learn random forest model into memory and provides a function to run a user through the model. Currently this expects just one user at a time and returns a single result, but the `predict_proba` function accepts a dataframe and returns a list so it could run multiple users at a time with a few tweaks.

`api/finalized_rfmodel.sav` This file is the random forest model we have trained. The model class loads it into memory and can make predictions off of it.

`api/api.py` A simple flask server that contains a single post endpoint expecting the schema defined in the schema class and returns a json of the score and classification. We classify someone as a scammer if the score is higher than 0.7. This is set at the top of the file. This file contains the helper functions needed to parse the raw data, generate features needed, and turn it into a dataframe the model can understand. The api runs on port 5000.

### cleaned_data
This contains the sparking clean data. The `cleaned_data/non-scammer` and `cleaned_data/scammer` contain data that has had json strings fixed, line endings fixed, and other small fixes.
The files in `cleaned_data` are the joined data from the non-scammer and scammer folders. A scammer column is added to maintain the labels. `cleaned_data/all.csv` and `cleaned_data/all-noprompt.csv` are our final datasets we worked with the five other datasets joined to their user. We ended up not using the prompt dataset in our model, hence the `cleaned_data/all-noprompt.csv` file. `cleaned_data/all-noprompt.csv` is the data file the saved model the api uses is trained on.

### Datasets and large_datasets
These are the raw data files we were sent. The large datasets is what the `cleaned_data` files come from.

## Root directory - misc scripts and files
`Cleaned_user_scammer.Rmd`: an R script for exploratory data analysis on the user scammer data

`finalized_rfmodel.sav`: This is where the script that creates the model puts the file. Didn't want it accidently overwriting a working model in the api.

`join.py`: This is responsible for merging the separate cleaned datasets into a single dataset joining each on the user id. It removes unnecessary columns, renames columns, and generates new columns based on several features. 

`merge_data.py`: Somewhat more robust than `join.py` this script merges a `scammer` directory and a `non_scammer` directory and puts it in an output file

Run the script:
```
  merge_data.py ./cleaned_data/scammer ./cleaned_data/non-scammer ./cleaned_data
```

This script will check that there is a corresponding file in each directory and will exit if not. i.e. there needs to be a non-scammer photo file and a scammer photo file. It also assumes that each file begins with the dataset it came from (i.e. photo_nonscammer, profile_verification) and uses underscores instead of dashes in the name. It will output the new data files to the provided directory named with ALL.csv as the last part of the name. i.e. photoALL.csv, taglineALL.csv. It does **not** join the datasets into a single file.

`RFM Complete.iypnb`: This is a jupyter notebook that reads in the cleaned data and creates a random forest model using the sklearn library. It does some last minute tweaking of the data (this is handled in the api too), splits the data into train and test sets and trains the model. The cells after training help to evaluate the models performance including a confusion matrix, statistics, graphs, and ranking feature importance. Finally the last cells save the model to a file. This is the complete and final model we came up with.

`RFM Demo.iypnb`: This was our first attempt at the model and was what we used in our demo midway through the semester. Most of this code is handled by the other scripts and we have reduced the number to features greatly since this model.

`to_json.py`: This file servers to fix the json strings in the raw datasets. Because most of the columns used double quotes parsers could not handle the `analyze_data` column. We solved that by replacing the starting and ending quotes with two double quotes. `"` => `""`. This allows pandas, excel, and most other parsers to read the file correctly. There were still a few lines where the line endings caused problems, the amount of that was small enough that we manually removed those lines.

Run the script:
```
  ./to_json.py ./large_datasets/Scammers/photo_scammer.csv ./large_datasets/Scammers/photo_scammer_to_json.csv
```
You can overwrite the existing file with this, but the script will ask your permission first. This also is limited in that it assumes there is only one json string per row. It just looks for the first '{' and last '}' to know what characters to change.

`userpromptdatacleaning.iypnb`: This file is another jupyter notebook where we did some natural language processing on the prompt dataset. Could be useful if you decide to reincorporate the prompt data into the model, but we found it didn't make a significant difference and drastically increased the number of features needed. (One hot encoding for each word)

## The End
That's a brain dump of everything we have and we hope we have commented our code well enough that you can keep building off of this. Please feel free to email us if you have any questions. Thank you!
