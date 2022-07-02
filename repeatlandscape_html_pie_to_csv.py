#!/Users/kosukekataoka/anaconda3/bin/python
import sys
import re
import argparse
import pandas as pd

def class_extract(subclass):
    if '/' in subclass:
        idx = subclass.find('/')
        return subclass[:idx]
    else:
        return subclass

def generate_pie_df(line):
    line = line[1:-2].split(", ")
    df = pd.DataFrame(data={'Subclass': [line[0].replace("'",'')]})
    df['bp'] = line[1]
    df['Class'] = class_extract(line[0].replace("'",''))
    return df

def generate_pie_unmasked_df(line):
    line = line[1:-2].split(",")
    df = pd.DataFrame(data={'Subclass': [line[0].replace("'",'')]})
    df['bp'] = line[1]
    df['Class'] = class_extract(line[0].replace("'",''))
    return df

use = '\n'\
    '        python repeatlandscape_html_pie_to_csv.py -l repeatlandscape.html -s speceis_name'
des = 'Convert from RepeatLandscape html result file to csv format file.'\
    '\nA file named as YOUR_SPECIES_repeatlandscape.csv will be generated in your current directory.'

psr  = argparse.ArgumentParser(
    prog = 'repeatlandscape_html_pie_to_csv',
    usage = use,
    description = des,
    formatter_class=argparse.RawTextHelpFormatter
    )

psr.add_argument('-l', '--landscape', required=True, help='RepeatLandscape html format result file. Required.')
psr.add_argument('-s', '--species', required=True, help='Speceis name. Required.')

args = psr.parse_args()

html_in = args.landscape
species = args.species

# html_in = sys.argv[1]
# species = sys.argv[2]

cnt_p = 0
pattern_pieData_addRows = re.compile(r'^pieData\.addRows\(\[')
pattern_pieData_end = re.compile(r'\]\);')
df_pie_out = pd.DataFrame(columns=['Class', 'Subclass', 'bp'])

with open(html_in, 'r') as html:
    for line in html:
        if bool(
            pattern_pieData_addRows.search(line.strip())
            ) == True:
            cnt_p += 1
        elif cnt_p != 0 and line.strip()[0:2] == "['" and line.strip()[0:5] != "['Unm":
            # print(line)
            df = generate_pie_df(line.strip())
            df_pie_out = pd.concat([df_pie_out, df], axis=0)
        elif cnt_p != 0 and line.strip()[0:5] == "['Unm":
            df = generate_pie_unmasked_df(line.strip())
            df_pie_out = pd.concat([df_pie_out, df], axis=0)
        elif cnt_p != 0 and bool(
            pattern_pieData_end.search(line.strip())
            ) == True:
            break

df_pie_out['Species'] = species

df_pie_out.to_csv('./'+ species + '_repeatlandscape_pie.csv', index=False)
