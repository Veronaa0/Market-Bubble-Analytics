import pandas as pd

data= {
    "Bubble": ["Dot-Com", "Housing", "Crypto", "AI"],
    "Year": [2000, 2008, 2021, 2026]
}

df=pd.DataFrame(data)

print(df)
print(df["Bubble"])
print(df["Year"].mean())