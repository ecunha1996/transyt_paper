import os
import pandas as pd


def main():
    text_file = open(r"kegg_compounds.txt", "r")
    lines = text_file.readlines()
    text_file.close()
    # create dataframe:
    df = pd.DataFrame(data = lines,columns=['external_identifier'])
    df['external_identifier'] = df['external_identifier'].str.strip()
    df['name'] = df['external_identifier'].str.split(" ").str[1]
    df.to_csv(r"kegg_compounds.csv", index=False)




if __name__ == '__main__':
    # os.chdir(r"C:\Users\Bisbii\Desktop\TranSyt")
    main()