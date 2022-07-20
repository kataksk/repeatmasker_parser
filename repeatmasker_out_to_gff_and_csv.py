#!/Users/kosukekataoka/anaconda3/bin/python
import re
import argparse
# import pandas as pd

def class_extract(subclass):
    if '/' in subclass:
        idx = subclass.find('/')
        return subclass[:idx]
    else:
        return subclass

def print_plus_or_minus(input):
    if input == "+":
        out = input
    elif input == "C":
        out = "-"
    return out
    
use = 'python repeatmasker_out_to_gff_and_csv.py -i/--in repreatmasker_result.out -s/--species your_species'
des = 'Convert from *.out file of RepeatMasker to csv and gff format file.'

psr  = argparse.ArgumentParser(
    prog = 'repeatmasker_out_to_gff_and_csv',
    usage = use,
    description = des,
    formatter_class=argparse.RawTextHelpFormatter
    )

psr.add_argument('-i', '--input', required=True, help='*.out file of RepeatMasker. Required.')
psr.add_argument('-s', '--species', required=True, help='Species name. Required.')

args = psr.parse_args()

out_in = args.input
species = args.species

output = ''

with open(out_in, 'r') as f:
    for line in f:
        line = re.sub('\s', '\t', line.lstrip())
        line = line.split("\t")
        line = [s for s in line if s != '']
        if len(line) != 0:
            if line[0] == "SW" or line[0] == "score":
                continue
            else:
                output += line[4] + "\tRepeatMasker\t" + line[10] + "\t" + line[5] + "\t" + line[6] + "\t" + line[1] + "\t" + print_plus_or_minus(line[8]) + "\t.\t.\n"

# print(output)

file_name = species + '_repeat.gff'
f = open(file_name, 'w')
f.write(output)
f.close()

# df = pd.read_csv(file_name, sep='\t', names=('A', 'B', 'C', 'D'))
