import random


def generate_BP():
    systolic = random.randint(80, 170)
    diastolic = random.randint(60, 120)
    BP = str(systolic) + "/" + str(diastolic)
    print(BP)


generate_BP()
