'''
This python script can be ran alone using the command: python3 src/cmu_dict.py
User can search ApraBET pronounciation with it.
'''
import requests, re

URL = "https://raw.githubusercontent.com/Alexir/CMUdict/master/cmudict-0.7b"

def download_dict(url):
    '''
    This function takes the url of the CMU's Pronunciation Dictionary and returns
    the relevant lines
    '''
    print("Downloading CMUdict v0.07...")
    response = requests.get(url)
    if response.status_code == 200:
        contents = response.text
    else:
        print("Failed to download the file.")
    lines = contents.split("\n")

    # Dictionary starts from line 126 and the last 6 lines are irrelevant
    return lines[126: -6]

def tokenize_dict(lines):
    '''
    This function takes the relevant lines from the raw file and tokenize
    words and their respective pronounciations. Note that some words have
    more than one pronouncation. It then returns a dictionary with key-value 
    pairs as follows:
    {word: [pronounciation1, pronounciation2]}
    '''
    print("Tokenizing and building dictionary...")
    cmu_dict = dict()
    for line in lines:
        line = re.sub(r'\(\d+\)', '', line)
        word, pronounciation = line.split("  ")
        pronounciation = pronounciation.replace("\r", "")
        if word not in cmu_dict:
            cmu_dict[word] = [pronounciation]
        else:
            cmu_dict[word].append(pronounciation)

    return cmu_dict

def cmu_dictionary():
    '''
    This function calls the above functions and returns a "pythonized"
    CMU's Pronunciation Dictionary. See tokenize_dict() for more info.
    Note: this function is called by src/main.py to transform utterances.
    '''
    dictionary = download_dict(URL)
    dictionary = tokenize_dict(dictionary)

    return dictionary

def search(cmu_dict, word):
    '''
    This function takes a dictionary and a word and return a list of 
    possible pronounciation of the word.
    '''
    return cmu_dict[word.upper()]

def search_loop():
    '''
    This function loops the search().
    '''
    dictionary = cmu_dictionary()
    while True:
        word = input("Search for the word: ")
        if word.upper() in dictionary:
            print(search(dictionary, word))
        else:
            print(word + " not found")

if __name__ == "__main__":
    search_loop()