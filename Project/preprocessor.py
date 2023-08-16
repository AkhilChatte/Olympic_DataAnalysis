import pandas as pd
def preprocess(df, region):
    # Taking only summer olympics data
    df = df[df['Season'] == 'Summer']
    # merging data from region and df using NOC as key
    df = df.merge(region, on='NOC', how='left')
    df.drop_duplicates(inplace=True)
    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)
    return df