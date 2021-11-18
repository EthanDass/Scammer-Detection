import sys

read_file_path = sys.argv[1]
write_file_path = sys.argv[2] if len(sys.argv) > 2 else './out.csv'

if read_file_path == write_file_path:
  ans = input('Warning! This action will overwrite the source file. Are you sure you want to do this? (y/n)').lower()[0]

  if ans is not 'y':
    print('Exiting before converting file')
    exit()

# Read file into lines
read_file = open(read_file_path, 'r')
write_file = open(write_file_path, 'w')

count = 0
data = []

# Go line by line fixing the json
# This assumes there is only one json body per line
for line in read_file:
  new_line = ''
  # Assumes there is always a header line. Skip that
  if count is 0:
    new_line = line
  else:
    start = line.find('{')
    end = line.rfind('}')+1

    if start is -1: # json field is null
      new_line = line
    else:
      json = line[start:end]
      # replacing outer quotes in json with double double quotes
      # https://stackoverflow.com/questions/57977099/read-csv-with-json-feature
      json = json.replace('"', '""')

      new_line = f'{line[:start]}{json}{line[end:]}'

  data.append(new_line)
  count += 1


write_file.writelines(data)

read_file.close()
write_file.close()

print('Successfully converted file')