# CMPUT 461 Assignment #1: REGEX Data Cleaning, CHILDES

This assignment prepares data for the downstream task in a later assignment. This assignment is separate into two tasks: data cleaning and data transformation.

**Input:** Child Language Data Exchange System (CHILDES Talkbank)

**Output:** Transformed ApraBET pronunciation of the CHILDES transcript

## Task: Data Cleaning
We use a subset of the CHILDES data (in Data directory). The data contains transcripts from oral language that represent the language that young children are exposed to in everyday settings. The data is stored in .cha files. This format is specific to the CHILDES Talkbank data. The first task will be to convert the files to raw text and remove both the header and extraneous information. It then writes the clean data to the clean directory.

## Task: Transformation
The cleaned data from the first task is then transformed into ApraBET to represent sound. CMU's Pronunciation Dictionary is used to map words to pronunciations. 

**Note:** Justifications of decisions made during data cleaning and transformation is described in justification.txt.

## Example Sentences ##
The following table shows how the program transform utterances in the transcripts:
| Cleaned        | Tokenized           | Transformed  |
| ------------- |-------------| -----|
| what are you making ?     | ['what', 'are', 'you', 'making', '?'] | W AH1 T AA1 R Y UW1 M EY1 K IH0 NG ? |
| this is a medicine ?      | ['this', 'is', 'a', 'medicine', '?']      | DH IH1 S IH1 Z AH0 M EH1 D AH0 S AH0 N ?  |
| you see baby needta sleep . | ['you', 'see', 'baby', 'needta', 'sleep', '.']      | Y UW1 S IY1 B EY1 B IY0 [UNK] S L IY1 P .  |


**Note:** unrecognizable words are replaced with the [UNK] token

## Instructions
**1. Clone the repo**
```bash
git clone https://github.com/UOFA-INTRO-NLP-F21/assn1-regex-datacleaning-lokhimis.git
```

**2. Run the program**

This python script does not use any additional plugin and can be ran using the following command in the project root directory:
```bash
cd assn1-regex-datacleaning-lokhimis
python3 src/main.py
```
The main.py will recursively clean and transform input .cha files and output them in the clean and transformed directory.

**3. Finding output files**

The cleaned files are output to clean/ directory in the repository root and the transformed files are output to transformed/ directory. Both of the directories have the same directory structure as the Data directory. 

A file (unk.txt) containing words that are not in the CMU pronunciation dictionary generated during .cha processing and is output in the root directory.

## Contributor
| Full Name        | Student ID           | CCID|
| ------------- |-------------|---|
| Lok Him Isaac Cheng    | 1562295 | lokhimis |

Sites consulted:

https://childes.talkbank.org/

https://www.makeareadme.com/

## Generative AI Use ##
ChatGPT (https://chat.openai.com/) was used during development. It was mostly used on regex expression generation, syntax checking (during debugging), code structure drafting, idea exploration, and grammar checking (justifications.txt). 

## Additional information ##
Using the given subset of the CHILDES provided on GitHub Classroom, the program gives the following summary:
- Number of files processed  : 644
- Total number of words        : 1478448
- Total number of unique words : 11770
- Total number of unknown words: 1459
- Percentage of unknown words  : 0.0987%

## Additional feature ##

While the python script src/cmu_dict.py is designed to be a module called by the main.py, it can be ran alone as a regular dictionary program.

```bash
python3 src/cmu_dict.py
```

