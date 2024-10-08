import json

def add_saldo(item, path):
    with open(path, 'a') as file:
        item[1] = round(item[1], 3)
        file.write(f'{item[0]},{item[1]}' + "\n")

def load_saldo():
    data = []

    with open('db/saldo_GALAUSDT.txt', 'r') as file:
        lines = file.readlines()
        print('count saldo')
        for line in lines:
            if line != '':
                parts = line.strip().split(',')
                timestamp = float(parts[0])
                value = float(parts[1])
                data.append([timestamp, value])

    return data