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


start_dag_m1            = 0 
start_dag_m2            = 0 
start_dag_m3            = 0 

total_penalties         = 0
tt_m1                   = 0

volgorde_m1             = []
volgorde_m2             = []
volgorde_m3             = [] 

best                    = []




start_dag_m2            = 0
tot_tard_m2             = 0
volgorde_m2             = []

di_orders.sort(key=lambda job: job['Deadline'])
di_machines.sort(key=lambda machine: machine['Speed'], reverse=True)




def planning_machine(machine, orders):

    start_dag            = 0
    tot_tard             = 0
    volgorde             = []
    vorige_kleur         = None
    for order in orders:

        volgorde.append(order['Order'])
        
        kleur = order['Colour']
        

        #  extra tijd voor de kleurverandering
        if  vorige_kleur != None and kleur!= vorige_kleur:
            for setup in di_setups:
                if setup['From colour']==vorige_kleur and setup['To colour']==kleur:
                    start_dag+= setup['Setup time']
                    break

        # productietijd
        tijd = order['Surface']/machine['Speed']
        start_dag += tijd

        # tardiness
        if start_dag>order['Deadline']:
            tot_tard += start_dag-order['Deadline']
        vorige_kleur = kleur
    return start_dag, tot_tard, volgorde

tijdm2, tardm1, volgordem1 = planning_machine(di_machines[0], di_orders)
print(tijdm2, tardm1, volgordem1 )
