import pandas as pd
import os
import json
import numpy as np


path = './cleaned_data'

###### HELPER FUNCTIONS #######
# Returns bool of whether users age is within their preferred dating range
def get_in_age_range(row):
  l = row['pref_age_low']
  h = row['pref_age_high']
  age = row['age']

  if l is None and h is None:
    return False

  if l is None and age < h:
    return True

  if h is None and age > l:
    return True

  if age > l and age < h:
    return True

  return False

# Return the difference between lower and higher age preference
def get_age_range_size(row):
  l = row['pref_age_low']
  h = row['pref_age_high']

  if l is None or h is None:
    return None
  
  return h-l

def get_gender_from_face(row):
  faces = row['faces']

  if faces is None or isinstance(faces, float) or len(faces) == 0:
    return None

  # There could be multiple faces in a photo and the first might not be
  # the user. We don't know the best approach to this scenario so we're
  # just going to use the first face available
  return faces[0]['gender']

def get_age_from_face(row):
  faces = row['faces']

  if faces is None or isinstance(faces, float) or len(faces) == 0:
    return None

  # There could be multiple faces in a photo and the first might not be
  # the user. We don't know the best approach to this scenario so we're
  # just going to use the first face available
  return faces[0]['age']

# Returns whether the user's reported age matches the photo's age
def get_gender_diff(row):
  user_gender = row['gender']
  photo_gender = row['photo_gender']

  if user_gender is None or photo_gender is None:
    return None

  return user_gender == photo_gender

# Returns the difference between the photo's age and user's reported age
def get_age_diff(row):
  user_age = row['age']
  photo_age = row['photo_age']

  if user_age is None or photo_age is None:
    return None

  return photo_age - user_age

##### READ DATA FILES #####
photo = pd.read_csv(f'{path}/photoALL.csv').drop(columns=['id', 'scammer', 'created_at', 'deleted_at'], axis=1)
profile = pd.read_csv(f'{path}/profileALL.csv').drop(columns=['id', 'scammer', 'created_at'], axis=1)
tagline = pd.read_csv(f'{path}/taglineALL.csv').drop(columns=['id', 'scammer', 'created_at'], axis=1)
user = pd.read_csv(f'{path}/userALL.csv')
prompt = pd.read_csv(f'{path}/cleanedpromptALL.csv').drop(columns=['id', 'scammer', 'created_at'], axis=1)

# we will merge in dataframes to all with a left union to preserve the number or users
all = pd.DataFrame()

#region ##### User Data #####

# # Get basic user data
# boolean values for whether field is present
user_bool = pd.notnull(user[['fb_id', 'email', 'hometown', 'school', 'position', 'mission_location']])
# everything else needed
user_other = user[['user_id', 'age', 'gender', 'dating_interest', 'pref_age_low', 'pref_age_high', 'pref_search_radius', 'country_code', 'scammer' ]]

all = pd.concat([all, user_other], axis=1)
all = pd.concat([all, user_bool], axis=1)

# Get computed user data
# whether a user's age is in their age range
all['in_age_range'] = user.apply(lambda row : get_in_age_range(row), axis=1)
# boolean if ig connected
all['is_ig_connected'] = (user['is_ig_connected'] == 1).astype(bool)
# get the size of the age range
all['age_range_size'] = user.apply(lambda row : get_age_range_size(row), axis=1)
# boolean scammer label
all['scammer'] = (all['scammer'] == 'Yes').astype(bool)

#endregion


#region ##### Tagline Data #####
# num active tags, num deleted tags

# We only need user id and deleted at to count
tagline = tagline[['user_id', 'deleted_at']]

# tags that don't have a deleted at column are active
active_tags = tagline[tagline['deleted_at'].isna()]
deleted_tags = tagline[tagline['deleted_at'].notna()]

# Count the number of tags in each
deleted_tag_count = deleted_tags.groupby('user_id').size().to_frame('deleted_tag_count').reset_index()
active_tag_count = active_tags.groupby('user_id').size().to_frame('active_tag_count').reset_index()

# Merge counts to all on user_id
all = all.merge(active_tag_count, on='user_id', how='left')
all = all.merge(deleted_tag_count, on='user_id', how='left')
#endregion


#region ##### Photo data: ######
# r-score, adult content, adult-score, gender matches (compared to user), age diff (compared to user age)

# Fill in null analyze data so we can turn it into a json
photo['analyze_data'].fillna('{"isR":null,"rScore":null,"isAdultContent":null,"adultScore":null,"faces":null}', inplace=True)

# pull json into columns
temp = pd.json_normalize(photo['analyze_data'].apply(json.loads))
photo = photo.join(temp).drop('analyze_data', axis=1)

# Get number of photos per user
photo_count = photo.groupby('user_id').size().to_frame('photo_count').reset_index()

# Get average age and mode gender from photos for each user
photo['age'] = photo.apply(lambda row : get_age_from_face(row), axis=1)
photo['gender'] = photo.apply(lambda row : get_gender_from_face(row), axis=1)


average_age = photo.groupby('user_id')['age'].mean().reset_index().rename(columns={'age': 'photo_age'})
max_adult_score = photo.groupby('user_id')['adultScore'].max().reset_index()
max_rscore = photo.groupby('user_id')['rScore'].max().reset_index()
gender = photo.groupby('user_id')['gender'].apply(lambda x: x.mode()).reset_index().rename(columns={'gender': 'photo_gender'}).drop('level_1', axis=1)

all = all.merge(photo_count, on='user_id', how='left')
all = all.merge(average_age, on='user_id', how='left')
all = all.merge(max_adult_score, on='user_id', how='left')
all = all.merge(max_rscore, on='user_id', how='left')
all = all.merge(gender, on='user_id', how='left')

all['gender_diff'] = all.apply(lambda x : get_gender_diff(x), axis=1)
all['age_diff'] = all.apply(lambda x : get_age_diff(x), axis=1)
#endregion

#region ##### Profile Data #####
# only need pose_id
profile = profile[['user_id', 'pose_id']]
# Note: we wanted to keep pose_id, but it seems users can submit multiple photos without deleting previous ones
#       not sure how to incorporate into model yet, so going with the number of photos submitted for now
profile_count = profile.groupby('user_id').size().to_frame('profile_count').reset_index()

all = all.merge(profile_count, on='user_id', how='left')
#endregion

#region ##### Prompt Data #####
# delete duplicate rows
prompt = prompt[prompt['deleted_at'].isna()]

all = all.merge(prompt, on='user_id', how='left')
#endregion


print(all.info())

# Write to file
all.to_csv(f'{path}/all.csv', index=False)

