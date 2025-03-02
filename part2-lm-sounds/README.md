# Intro to NLP - Assignment 3

## Team
|Student name| CCID |
|------------|------|
|Lok Him Isaac Cheng   | lokhimis     |

## Task 1: Data Preparation
[Assginment 1](https://github.com/UOFA-INTRO-NLP-F21/assn1-regex-datacleaning-lokhimis) was improved based on the feedback on eClass. The lines in the transformed files are then randomly split into a [training set](/data/training.txt) (~80%) and a [dev set](/data/dev.txt) (~20%).

## Task 2: Training N-gram Models
The 3 classes Unigram, Bigram, and Trigram in [main.py](src/main.py) are responsible training respective classes of the given dataset. Correct amount of begin-of-utterance and end-of-utterance symbols are added when training bigram and trigram. Optional laplace smoothing are also implemented.

## Task 3: Evaluating N-gram Models
The evalution of n-gram models in this assignment is calculating the perplexity. The 3 classes have a method to calculate perplexities of (1) training set and (2) dev set. This metric is printed out at the end of execution.

## Data
- The [training](/data/training.txt) and [dev](/data/dev.txt) sets in the [data](data) directory.
- [all_transformed_lines.txt](data/all_transformed_lines.txt) in the data directory contains all the lines and this is the source file that generates the training and the dev sets.

## Execution
### Obtaining new splittings of training and dev sets
To obtain a new splitting of training and dev set (make sure all_transformed_lines.txt is placed in the data directory):

`python3 src/split_data.py`

### Executing the main program
[main.py](src/main.py) takes four command line arguments. The arguments include three positional arguments in this order: (1) one positional argument for model type (unigram/bigram/trigram), (2) one argument for the path to the training data, (3) one argument for the path to the data for which perplexity will be computed. In addition, (4) one optional argument for smoothing (--laplace) could be present.

`python3 src/main.py [n-gram type] [training set path] [dev set path] [optional --laplace]`

For example, to train a bigram with smoothing using the training set with a path of data/training.txt, dev set of data/dev.txt, the command would be:

`python3 src/main.py bigram data/training.txt data/dev.txt --laplace`

## Evaluation

|Model           | Smoothing  | Training set PPL | Dev set PPL |
|----------------|----------- | ---------------- | ----------- |
|unigram         | -          |  35.12429        |  35.1217    |
|bigram          | unsmoothed |  15.46624        |  15.45774   |
|bigram          | Laplace    |   15.55921       |  15.54493   |
|trigram         | unsmoothed |   7.90475        |  7.9021     |
|trigram         | Laplace    |  7.96067         |  8.03764    |
**Grad student extension**                                           
|bigram (KenLM)  | Kneser-Ney |   15.46952       | 15.4985     |
|trigram (KenLM) | Kneser-Ney |    7.93968       |  8.06683    |

*Figures are rounded to 5 decimal places.*

## Acknowledegement
**1. Desmos Scientific Calculator** 

https://www.desmos.com/scientific

**2. Official Python Documentation on collections module:** 

https://docs.python.org/3/library/collections.html

**3. Speech and Language Processing.  Daniel Jurafsky & James H. Martin. (Chapter 3)**

https://web.stanford.edu/~jurafsky/slp3/3.pdf

**4. N-Gram Language Model, Exercises using, Bi-Gram, Tri-gram & Four-gram, Natural Language Processing by Varsha's engineering stuff** 

https://www.youtube.com/watch?v=zz1CFBS4NaY&ab_channel=Varsha%27sengineeringstuff

## Generative AI Use
ChatGPT (https://chat.openai.com/) was used during development. It was mostly used on checking syntax of the collections module and consulted the behavior of the different classes of the module. It was consulted on design of multi-dimensional tables that stores counts using Python's built-in dictionary datatype, and loops that can access each variable inside these tables. ChatGPT was also consulted on the usage of reading in command line arguments using the built-in sys module. It was also used to check concepts and generate ideas when answering questions in the Graduate Student Extension part.

## TODOs

In this file you **must**:
- [x] Fill out the team table above. Please note that CCID is **different** from your student number.
- [x] Fill out the table in the [Evaluation](#evaluation) section.
- [x] Acknowledge all resources consulted (discussions, texts, urls, etc.) while working on an assignment. Non-detailed oral discussion with others is permitted as long as any such discussion is summarized and acknowledged by all parties.
- [x] Provide clear installation and execution instructions that TAs must follow to execute your code.