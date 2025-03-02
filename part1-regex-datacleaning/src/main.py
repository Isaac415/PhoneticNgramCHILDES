import re, os
import cmu_dict as cmu

NOT_IN_DICT = set()
ALL_WORDS = set()
TOTAL_WORD_COUNT = 0
FILE_NUM = int()


ALL_TRANSFORMED_LINES = list()


'''
TASK: Data Cleaning
'''

def read_file(filename):
    '''
    This function takes a filename and return the raw file content as a 
    list of lines.
    '''
    with open(filename, 'r', encoding='utf-8') as file:
        raw_content = file.readlines()
    return raw_content

def write_file(filename, content):
    '''
    This function takes in a filename and write cleaned content to it
    '''
    with open(filename, 'w', encoding='utf-8') as output_file:
        output_file.writelines(content)

def remove_header(content):
    '''
    This function takes in content (a list of lines) and return a list 
    of lines without header.
    '''
    header_pattern = r'^@.*'
    cleaned_content = list()
    for line in content:
        if not re.match(header_pattern, line):
            cleaned_content.append(line)
    return cleaned_content

def filter_conversation(content):
    '''
    This function takes in content (a list of lines) and return a list 
    of conversation lines (lines start with *)
    '''
    conversation_pattern = r'^\*.*'
    cleaned_content = list()
    for line in content:
        if re.match(conversation_pattern, line):
            cleaned_content.append(line)
    return cleaned_content

def remove_speaker_tag(content):
    '''
    This function takes in content (a list of lines) and return a list
    of conversation lines without the speaker tag
    '''
    speaker_tag_pattern = r'\*[A-Z]+:\s*'
    cleaned_content = list()
    for line in content:
        cleaned_line = re.sub(speaker_tag_pattern, "", line)
        cleaned_content.append(cleaned_line)
    return cleaned_content

def remove_extraneous_info(content):
    '''
    This function removes extraneous information and noises that is 
    irrelevant to the downstream task. The justification of choices
    is documentated in the justification.txt file. While some regex
    expression could be combined into a single one, I decided to 
    separate them for easier and more dynamically test and debugging.
    Here is a summary of what this function does:
    - remove ()
    - substitute text with explanation text dey [: they] -> they
    - remove [] (and content within)
    - remove <> (and content within)
    - remove tokens starting with &
    - remove +...
    - remove tokens that has @ in it
    - remove NAK tags and content within
    - remove xxx and yyy placeholders
    - remove _
    - remove -

    There are further cleanings that remove lines that are no longer
    relevant after cleaning:
    - remove empty lines
    - remove lines with 0 
    - remove leading ". . ." (appear due to the above cleaning)
    - replace sequence of spacebars into one single spacebar
    '''
    cleaned_content = list()
    for line in content:
        # Remove ()
        line = re.sub(r'\(([^)]+)\)', r'\1', line)
        # Substitute text with explaination text
        line = re.sub(r'(\w+) \[: (\w+)]', lambda x: x.group(2), line)
        # Remove [] including contents within
        line = re.sub(r'\[.*?\]', '', line)
        # Remove <> including contents within
        line = re.sub(r'\<.*?\>', '', line)
        # Remove tokens starting with &
        line = re.sub(r'&\S+\s*', '', line)
        # Remove +...
        line = re.sub(r'\+[^\s]*', '', line)
        # Remove NAK tag and content within
        line = re.sub(r'[^]*', '', line)
        # Remove xxx and yyy placeholders
        line = re.sub(r'\b(?:xxx|yyy)\b', '', line)
        # Remove all :
        line = re.sub(r':', '', line)
        # Remove all - and _
        line = re.sub(r'[-_]', ' ', line)
        # Remove all tokens with @ 
        line = re.sub(r'\S*@\S*', '', line)

        # Remove leading ". . ." (appear due to the above cleaning)
        line = re.sub(r'^[.\s]*', '', line)
        # Replace sequence of spacebars into one single spacebar
        line = re.sub(r'[ \t]+', ' ', line)
        # Remove empty lines and lines with "0"
        if re.search(r'0', line) or not re.search(r'[a-zA-Z]', line):
            continue

        '''
        Record all tokens in lines and prep for transformation
        '''
        words = line.split(" ")
        for word in words:
            global TOTAL_WORD_COUNT
            TOTAL_WORD_COUNT += 1
            ALL_WORDS.add(word)

        # Add cleaned line to cleaned_content
        cleaned_content.append(line)

    return cleaned_content

def clean_file(filename):
    '''
    This function is where the data pipelining happens. The flow
    as follows:
    (1) Read file
    (2) Remove header 
    (3) Filter out conversation lines
    (4) Remove speaker tags
    (5) Remove extraneous information
    It then returns the cleaned content (as a list of lines)
    '''
    content = read_file(filename)
    content = remove_header(content)
    content = filter_conversation(content)
    content = remove_speaker_tag(content)
    content = remove_extraneous_info(content)

    return content

def clean_cha_file(file_path):
    '''
    This function takes a file path (from Data) and calls clean_file() to 
    process the .cha file. It then writes the clean data into a .txt file
    in the required path (same structure as the Data folder)
    '''
    source_dir = "Data"
    clean_dir = "clean"

    # Generate the destination file path in the clean directory
    clean_file_path = file_path.replace(source_dir, clean_dir).replace(".cha", ".txt")
    os.makedirs(os.path.dirname(clean_file_path), exist_ok=True)

    # Clean .cha files and write file to the designated folder
    cleaned_content = clean_file(file_path)
    print("Processing: " + str(clean_file_path))
    write_file(clean_file_path, cleaned_content)

def clean_cha_files():
    '''
    This function recursively walk through the Data directory and calls
    clean_cha_file to clean the data file whenever it detects one. It 
    then prints out the total number of .cha files processed.
    '''
    print("Task: Data Cleaning")
    count = 0
    # Recursively process .cha files
    for root, _, files in os.walk("Data"):
        for file in files:
            if file.endswith(".cha"):
                file_path = os.path.join(root, file)
                clean_cha_file(file_path)
                count += 1
                
    print(f"Total .cha files cleaned: {count}")

'''
Task: Transformation
'''
def contains_number(string):
    return any(char.isdigit() for char in string)

def contains_alphabet(string):
    return any(char.isalpha() for char in string)

def transform_token(token, dictionary):
    '''
    This function transform a single token into pronunciation using
    the CMU's Pronunciation Dictionary and return the ApraBET
    representation of the pronunciation. It preserves punctuation,
    remove leading and trailing punctuation (if any) and check if 
    the token ends with apostrophe s ('s) (please see justification.txt
    for more info). [UNK] tokens will be added to be a placeholder 
    for words that are not present in the dictionary.
    '''
    if contains_number(token):
        return ""

    # Preserves single character punctuation
    if (len(token) == 1) and (bool(re.match(r'^[^a-zA-Z]$', token))):
        return ""

    # Remove leading and trailing puncuation
    token = re.sub(r"^[^a-zA-Z]+|[^a-zA-Z]+$", "", token)

    # Check if the token ends with apostrophe s
    apostrophe = False
    if re.search(r"'s$", token, flags=re.IGNORECASE):
        apostrophe = True
        token = re.sub(r"\'s$", '', token, flags=re.IGNORECASE)
    if token.upper() not in dictionary:
        NOT_IN_DICT.add(token.upper())
        return "<UNK> "
    elif (token.upper() in dictionary) and (apostrophe == False):
        return dictionary[token.upper()][0] + " "
    elif (token.upper() in dictionary) and (apostrophe == True):
        return dictionary[token.upper()][0] + " Z "

def transform_file(file_path, dictionary):
    '''
    This function takes in a file path name and dictionary and transform
    the file line by line. It returns the transformed content (as a list 
    of lines).
    '''
    # Read cleaned content
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_content = file.readlines()

    global ALL_TRANSFORMED_LINES
    transformed_content = list()

    # Transform line by line
    for line in raw_content:
        transformed_line = str()
        # Tokenize the line
        tokens = list(filter(None, line[:-1].split(" ")))
        for token in tokens:
            transformed_line += transform_token(token, dictionary)
        transformed_line = transformed_line + "\n"
        transformed_content.append(transformed_line)
        if contains_alphabet(transformed_line) and "<s> <s> </s>" not in transformed_line:
            ALL_TRANSFORMED_LINES.append(transformed_line)

        #print(line[:-1])
        #print(tokens)
        #print(transformed_line)

    return transformed_content

def transform_cha_file(file_path, dictionary):
    '''
    This function takes a file path (from clean) and calls transform_file() to 
    process the .txt file. It then writes the transformed data into a .txt file
    in the required path (same structure as the Data folder)
    '''
    source_dir = "clean"
    clean_dir = "transformed"

    # Generate the destination file path in the transform directory
    transform_file_path = file_path.replace(source_dir, clean_dir)
    os.makedirs(os.path.dirname(transform_file_path), exist_ok=True)

    # Clean .txt files and write file to the designated folder
    transformed_content = transform_file(file_path, dictionary)
    print("Processing: " + str(transform_file_path))
    write_file(transform_file_path, transformed_content)

def transform_cha_files():
    '''
    This function recursively walk through the clean directory and calls
    transform_cha_file to transform the data file whenever it detects one. 
    It then prints out the total number of .txt files processed.
    '''
    print("Task: Transformation")
    count = 0
    dictionary = cmu.cmu_dictionary()
    # Recursively process .txt files
    for root, _, files in os.walk("clean"):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                transform_cha_file(file_path, dictionary)
                count += 1
    
    global FILE_NUM
    FILE_NUM = count
    print(f"Total .txt files transformed: {count}")

def summary():
    '''
    This function prints out the summary and also output the unknown 
    words to unk.txt.
    '''
    print("\nNumber of files processed  : " + str(FILE_NUM))
    print("Total number of words        : " + str(TOTAL_WORD_COUNT))
    print("Total number of unique words : " + str(len(ALL_WORDS)))
    print("Total number of unknown words: " + str(len(NOT_IN_DICT)))
    percentage = 100 * len(NOT_IN_DICT)/TOTAL_WORD_COUNT
    print("Percentage of unknown words  : " + str(round(percentage, 4)) + "%")
    
    with open('unk.txt', 'w') as f:
        for line in NOT_IN_DICT:
            f.write(f"{line}\n")
    print("Unknown words are in unk.txt")

if __name__ == "__main__":
    clean_cha_files()
    transform_cha_files()
    summary()
    print(ALL_TRANSFORMED_LINES)
    print(len(ALL_TRANSFORMED_LINES))
    with open("all_transformed_lines.txt", "w") as file:
        for line in ALL_TRANSFORMED_LINES:
            file.write(line)