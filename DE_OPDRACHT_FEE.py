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

di_orders_org = dictionary(df_orders)
di_orders = di_orders_org.copy()
di_machines_org = dictionary(df_machines)
di_machines = di_machines_org.copy()
di_setups_org = dictionary(df_setups)
di_setups = di_setups_org.copy()


start_dag_m1            = 0 
start_dag_m2            = 0 
start_dag_m3            = 0 

total_penalties         = 0
total_tardiness         = 0

volgorde_m1             = []
volgorde_m2             = []
volgorde_m3             = [] 

best                    = []

di_orders.sort(key=lambda job: job['Deadline'])

