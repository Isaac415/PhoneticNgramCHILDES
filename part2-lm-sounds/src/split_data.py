import random

def roll_dice(probability=0.8):
    '''
    This function returns True with the given probability (default is 0.8),
    False with 1 - given probability.
    '''
    return random.random() < probability

def split_data():
    '''
    This function reads in data from data/all_transformed_lines.txt, split
    them into training set and dev set with the given probability, and write
    them into data/training.txt and data/dev.txt.
    '''
    # Read in file
    with open("data/all_transformed_lines.txt", "r") as file:
        data = file.readlines()
    
    # Split into training and dev sets
    training = list()
    dev = list()
    for line in data:
        if roll_dice():
            training.append(line)
        else:
            dev.append(line)
    
    # Write them into respective files
    with open("data/training.txt", "w") as file:
        for line in training:
            file.write(line)

    with open("data/dev.txt", "w") as file:
        for line in dev:
            file.write(line)    

    # Print statistics
    print("Total number of lines: " + str(len(data)))
    print("Number of training lines: " + str(len(training)))
    print("Number of dev lines: " + str(len(dev)))
    print("Percentage of training lines: " + str(round(100 * len(training) / len(data), 2)) + "%")
    print("Percentage of dev lines: " + str(round(100 * len(dev) / len(data), 2)) + "%")

if __name__ == "__main__":
    split_data()