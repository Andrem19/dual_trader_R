import json

def add_saldo(item, path):
    with open(path, 'a') as file:
        item[1] = round(item[1], 3)
        file.write(f'{item[0]},{item[1]}' + "\n")

def load_saldo():
    data = []

    with open('db/saldo_DOTUSDT.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(',')
            timestamp = float(parts[0])
            value = float(parts[1])
            data.append([timestamp, value])

    return data