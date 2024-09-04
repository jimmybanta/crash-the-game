

gpt_35_turbo = {
    'input': .0000005,
    'output': .00000150,
}

def calculate_price(model, input_length, output_length):
    return (model['input'] * input_length) + (model['output'] * output_length)

if __name__ == '__main__':
    price = calculate_price(gpt_35_turbo, 371, 1561)
    
    print(price)