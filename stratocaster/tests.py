#I got it working using tuple addition, here's an attempt at explaining.

column_titles = ['latitude', 'depth', 'mag', 'gap']

>>> load_numerical_data('earthquakes-proj8'.csv, column_titles)


# give each data_dict entry a value of tuple() for subsequent tuple addition using a loop. data_dict[0] = tuple() as a single line for explanation purpose.

data_dict[0] = tuple()

# iterating through the csv file converted into a list of dictionaries for each entry (row) in order to access values based off each column_titles title.

for row in list_of_row_dictionaries:

  # iterating through each title in the list of titles to get all      the required column values for each entry

  for title in column_titles:

    # continue updating the dictionary entry using tuple addition

    data_dict[0] = data_dict[0] + (row[title])


#would iterate as

data_dict[0] = ()
data_dict[0] = ('38.2553', )
data_dict[0] = ('38.2553', '101.43')
data_dict[0] = ('38.2553', '101.43', '4,3')
data_dict[0] = ('38.2553', '101.43', '4.3', '130')

#and return as 

{0: ('38.2553', '140.7112', '4.3', '130')}

would need to also convert strings at some point.
