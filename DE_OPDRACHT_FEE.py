import pandas as pd
import numpy as np
import random
import math as m

random.seed(42)

df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name = None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

def dictionary(df):

    jobs = []

    for i in range(len(df)):
        job = {}

        for column in df.columns:
            job[column] = df[column][i]

        jobs.append(job)

    return jobs

di_orders = dictionary(df_orders)
di_machines = dictionary(df_machines)
di_setups = dictionary(df_setups)


start_dag               = 0 
total_penalties         = 0
total_tardiness         = 0
volgorde_m1             = []
volgorde_m2             = []
volgorde_m3             = []
best                    = []

di_orders.sort(key=lambda job: job['Deadline'])

for machine in di_machines:
    print(machine['Speed'])