import time
import datetime

def dia_mes_ano():
    yy=(datetime.datetime.now()).year
    mm=(datetime.datetime.now()).month
    dd=(datetime.datetime.now()).day
    return f'{yy}/{mm}/{dd}'

def hora_min():
    min=time.strftime("%M")
    hora=time.strftime("%H")
    seg=time.strftime("%S")
    return f'{hora}:{min}:{seg}'
