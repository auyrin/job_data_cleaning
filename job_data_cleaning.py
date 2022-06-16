import numpy as np
import pandas as pd
np.set_printoptions(suppress = True)

data = pd.read_csv('raw_data.csv')

df = data.copy()

df.info()



drop unneccessary columns

df.drop(labels = ['country','country_code','has_expired','job_board','page_url','uniq_id'], axis = 1, inplace = True)



format the jobtype column

df['job_type'].unique()

df['job_type'][df['job_type'].str.contains('Intern', na = False)] = 'Intern'
df['job_type'][df['job_type'].str.contains('Contract', na = False)] = 'Contract'
df['job_type'][df['job_type'].str.contains('Per Diem', na = False)] = 'Per Diem'
df['job_type'][df['job_type'].str.contains('Full Time', na = False)] = 'Full Time'
df['job_type'][df['job_type'].str.contains('Part Time', na = False)] = 'Part Time'

df['job_type'] = df['job_type'].str.split(',').str[0].str.strip()

#delete the unwanted rows from the data. cause i dont need empty of meaningless rows in job_type
df = df[df['job_type'].str.contains('Intern|Contract|Per Diem|Full Time|Part Time', na = False)]



create a checkpoint

def checkpoint(filename, header, data):
    np.savez(filename, header = header, data = data)
    saved_data = np.load(filename+'.npz', allow_pickle = True)
    return (saved_data)

cols = np.array(df.columns)
cols_data = np.array(df)

test_file = checkpoint('test-file', cols, cols_data)

checkpoint_df = pd.DataFrame(test_file['data'], columns = test_file['header'])



format the job_title column

df['job_title']

# format the contents to my taste
for i in '|-':
    df['job_title'] = df['job_title'].str.split(i).str[0].str.split('Job in').str[0].str.strip()

#remove the unnecessary words from the job_title
df['job_title'][df['job_title'].apply(lambda x: len(x) > 30)] = df['job_title'].str.split('Job Application for').str[1]



go through all the unique values of a column

l = df['organization'].unique() # can be any column
unique_values = {}
for k in range(len(l)):
    unique_values[k] = l[k]



location and organization

df['location'].unique()

# swap rows for location column and job_description column
l = df['location'].unique()
for i in df['organization'].keys():
    if (df['organization'][i] in l):
        temp = df['location'][i]
        df['location'][i] = df['organization'][i]
        df['organization'][i] = temp

# format the contents to my taste
df['location'][df['location'].apply(lambda x: len(x) < 27 )] = df['location'].str.split(',').str[0]

df = df[df['location'].apply(lambda x: len(x)<27)]

df['location']

pattern = r'[a-zA-Z]'
df = df[df['location'].str.contains(pattern)]

#remove the rows with contact details
df = df[(df['location'].str.contains('Contact name|Phone')) == False]



df['organization'].unique()

df['organization'] = df['organization'].fillna('missing')

df['organization'][df['organization'].apply(lambda x: len(x) > 90)] = 'missing'

pattern = r'[0-9]'
df['organization'][df['organization'].str.contains(pattern)] = 'missing'

df['organization'][df['organization'].apply(lambda x: len(x) < 4)] = 'missing'

df['organization'][df['organization'].apply(lambda x: x == 'missing')] = np.nan



format salary column

df['salary'].unique()

# return min and max of the hourly salaries
def min_max_salary_hourly(value):
    if pd.isnull(value):
        return np.nan
    elif '/hour' in value:
        k = value.split('$')[0].strip()
        if '-' in k:
            mn = k.split('-')[0].strip()
            mx = k.split('-')[1].strip()
            try:
                mn = float(mn.replace(',', '').strip())
                mx = float(mx.replace(',', '').strip())
            except:
                return np.nan
            return mn, mx
    else:
        return np.nan

def min_max_salary_yearly(value):
    if pd.isnull(value):
        return np.nan
    elif '/year' in value:
        k = value.split('$')[0].strip()
        if '-' in k:
            mn = k.split('-')[0].strip()
            mx = k.split('-')[1].strip()
            try:
                mn = float(mn.replace(',', '').strip())
                mx = float(mx.replace(',', '').strip())
            except:
                return np.nan
            return mn, mx
    else:
        return np.nan

# add new columns for hourly and yearly salaries
df = df.assign(min_max_hourly_salary = df['salary'].apply(min_max_salary_hourly),
          min_max_yearly_salary = df['salary'].apply(min_max_salary_yearly)
         )

df = df.assign(median_hourly_salary = df['min_max_hourly_salary'].apply(lambda x: (x[0] + x[1]) / 2 if pd.notnull(x) else x))

df = df.assign(median_yearly_salary = df['min_max_yearly_salary'].apply(lambda x: (x[0] + x[1]) / 2 if pd.notnull(x) else x))



sector column

# i could remove all missing values in sector, to make our data cleaner; in this case i won't.
# for this data i priotised the job_type, job_decription, and location columns.
# if i wanted to make analysis about the sectors then i would priotise it also.

df['sector'].unique()

df['sector'][df['sector'].apply(lambda x: len(x) > 90 if pd.notnull(x) else False)] = np.nan

colz = ['date_added','job_description', 'job_title', 'job_type', 'location',
           'organization', 'salary', 'min_max_yearly_salary', 'median_hourly_salary', 'median_yearly_salary', 'sector']

df = df[colz]

df.to_csv('cleaned_data.csv')
