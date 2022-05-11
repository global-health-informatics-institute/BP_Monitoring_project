BP = '802C504855'
data = list(BP)
if len(BP) == 10:
    dia_mmHg = int(data[4] + data[5], 16)
    x = int(data[2] + data[3], 16)
    sys_mmHg = dia_mmHg + x
    print(sys_mmHg)
    print(dia_mmHg)


