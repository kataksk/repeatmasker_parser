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

def generate_df(line):
    line = line[1:-2].split(", ")
    df = pd.DataFrame(line[1:], columns = ['Percent'])
    df['Kimura'] = line[0].replace("'",'')
    return df
use = '\n'\
    '        python repeatlandscape_html_to_csv.py -l repeatlandscape.html -s speceis_name'
des = 'Convert from RepeatLandscape html result file to csv format file.'\
    '\nA file named as YOUR_SPECIES_repeatlandscape.csv will be generated in your current directory.'

psr  = argparse.ArgumentParser(
    prog = 'repeatlandscape_html_to_csv',
    usage = use,
    description = des,
    formatter_class=argparse.RawTextHelpFormatter
    )

psr.add_argument('-l', '--landscape', required=True, help='RepeatLandscape html format result file. Required.')
psr.add_argument('-s', '--species', required=True, help='Speceis name. Required.')
psr.add_argument('--ggplot', help='Output ggplot file.', action="store_true")

args = psr.parse_args()

html_in = args.landscape
species = args.species

# html_in = sys.argv[1]
# species = sys.argv[2]

pattern_addColumn = re.compile(r'^data\.addColumn\(\'number\',')
subclass = list()

with open(html_in, 'r') as html:
    for line in html:
        if bool(
            pattern_addColumn.search(line.strip())
            ) == True:
            subclass.append(
                line.strip().strip("data.addColumn('number', '").strip("');").strip()
                )

subclass_df = pd.DataFrame(subclass, columns = ['Subclass'])

for i in range(len(subclass)):
    subclass[i] = class_extract(subclass[i])

class_df = pd.DataFrame(subclass, columns = ['Class'])
merged_class_df = pd.merge(subclass_df, class_df, right_index=True, left_index=True)

cnt = 0
pattern_addRows = re.compile(r'^data\.addRows\(\[')
pattern_pieData = re.compile(r'^pieData')
df_out = pd.DataFrame(columns=['Percent', 'Kimura', 'Subclass', 'Class'])

with open(html_in, 'r') as html:
    for line in html:
        if bool(
            pattern_addRows.search(line.strip())
            ) == True:
            cnt += 1
        elif cnt != 0 and line.strip()[0:2] == "['":
            df = generate_df(line.strip())
            df = pd.merge(df, merged_class_df, right_index=True, left_index=True)
            df_out = pd.concat([df_out, df], axis=0)
        elif cnt != 0 and bool(
            pattern_pieData.search(line.strip())
            ) == True:
            break

# print(df_out)

df_out.to_csv('./'+ species + '_repeatlandscape.csv', index=False)

# df_out = df_out.reset_index()
# print(df_out)

####

if args.ggplot:
    import pyper
    r = pyper.R(use_pandas='True')
    r.assign("df_out", df_out)
    r("""
    library(ggplot2)
    library(shiny)
    
    ggplot(csv, aes(x=Kimura, y=Percent, fill=factor(Class, levels=c("SINE", "LINE", "LTR", "DNA", "RC", "Unknown"))))+
    geom_col()+
    xlab("Kimura substition level (CpG adjusted)")+
    ylab("Percent of genome (%)")+
    labs(fill="Class")+
    scale_fill_manual(values=c("#00B5F8", "#398120", "#FFB137", "#FF744E", "#FF1988", "#778180"))
    
    ggsave("test.png", dpi=300,  device="png")

    getwd()

    b64image <- base64enc::dataURI(file = "test.png", mime = "image/png")
    """)
    res = r.get("b64image")
    print(res)
