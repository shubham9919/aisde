import pandas as pd

df = pd.read_excel("First_300.xlsx")

df = df.iloc[2:, 1:3]

# print(df.iloc[:, 0])
companies = df.iloc[:, 0].to_list()
hostnames = df.iloc[:, 1].to_list()
for i in range(len(hostnames)):
    hostnames[i] = hostnames[i].replace("https://", "")
    hostnames[i] = hostnames[i].replace("http://", "")
    hostnames[i] = hostnames[i].split("/")[0]
print(companies)
print(hostnames)


def get_comp_hostnames():
    df = pd.read_excel("First_300.xlsx")

    df = df.iloc[2:, 1:3]
    companies = df.iloc[:, 0].to_list()
    hostnames = df.iloc[:, 1].to_list()
    for i in range(len(hostnames)):
        hostnames[i] = hostnames[i].replace("https://", "")
        hostnames[i] = hostnames[i].replace("http://", "")
        hostnames[i] = hostnames[i].split("/")[0]

    return companies, hostnames
