import os

target_dir = r'C:\Users\cyh\Desktop\copy\Export_Output.txt'
fotolog_dir = r'C:\Users\cyh\Desktop\copy\foto_log'

count =0
with open(target_dir) as txt:
    for lines in txt:
        data = lines.split(',')
        if os.path.isfile(data[9]):
            pass
        else:
            print data[9]
            count +=1

print count