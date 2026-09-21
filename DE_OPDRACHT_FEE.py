import pandas as pd
import numpy as np
import random
import math as m

random.seed(42)

df = pd.read_excel('PaintShop-September2026.xlsx')


def dictionary(df):

    jobs = []

    for i in range(len(df)):
        job = {}

        for column in df.columns:
            job[column] = df[column][i]

        jobs.append(job)

    return jobs


jobname = []
processingtime = []
duedate = []
for i in df['JobName']:
    jobname.append(i)
for i in df['ProcessingTime']:
    processingtime.append(i)
for i in df['DueDate']:
    duedate.append(i)

#greedy methode
dag = 0 
totaltardiness = 0
volgorde = []
best = []
for i in range(len(jobname)):
    k = duedate.index(min(duedate))
    dag+= processingtime[k]
    if dag>duedate[k]:
        totaltardiness+= -(duedate[k]-dag)
    volgorde.append(jobname[k])
    jobname.pop(k)
    duedate.pop(k)
    processingtime.pop(k)

best = volgorde.copy()
best_tardiness = bereken_tardiness(best, jobs)
current = best.copy()

print(best, best_tardiness)
