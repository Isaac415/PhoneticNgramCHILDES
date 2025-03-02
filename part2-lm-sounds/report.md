# Assignment 3 Report
## Task 1 - Data Preparation
The transformed dataset is further processed according to the feedback of Assignment 1. As indicated in the feedback, only the removal of digits is needed. As stress indicators was not present in the dataset, stress of pronounciation is not trained in the n-gram models. Word boundaries marks are not added to the dataset, i.e. the relationship between pronounciations of words are also considered during training, and has an effect on pronounciation predictions. 

The contents are remained one utterance per line in the files and then all lines in the files are funneled into a single large source file: all_transformed_lines.txt in the data directory. The script split_data.py splits this large file into two txt files containing the training set (80% of all the lines) and the dev (20% of all the lines).

## Task 2 - Training N-gram Models
The process data in Task 1 is then used to train the n-gram models. Some further treatment (specific to n-gram type) within the preprocessing step of training are performed.

### Begin-of-utterance and end-of-utterance
The begin-of-utterance `<s>` and end-of-utterance `</s>` marks were not directly added to the dataset, instead, they are added to the local variable which stores data lines during a short preprocess step in the process_dataset() method of the Bigram and Trigram class. 

* **Unigram**: no begin-of-utterance nor end-of-utterance mark were added
* **Bigram**: one begin-of-utterance and one end-of-utterance mark were added
* **Trigram**: two begin-of-utterance and one end-of-utterance mark were added

They are then treated as regular tokens and then be trained in the training process. This way, the model can handle and correctly estimate the probabilities of tokens that are present in the begin of utterance and end of utterance.

### Out-Of-Vocabulary (OOV) handling
The OOV handling method was strictly following the second alternative illustrated in 3.4.1 Unknown Words in Speech and Language Processing. Phonetic tokens with fewer than 30 occurances are replaced with the token `<UNK>`. Then proceed to train the language model as before, treating `<UNK>` as a regular word. Any token that is not seen in the training set is treated as `<UNK>` during evaluation. This way, the model can handle unseen tokens in the dev set.

## Task 3 - Evaluating N-gram Models
No further decision (and thus justification) has to be made in this task. 
Here is the perplexities calculated:

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



## Graduate Student Extension - KenLM
### Key Problems Addressed by KenLM
**Begin by identifying the primary challenges that KenLM aims to tackle. What are the main issues or limitations that KenLM endeavors to solve in the realm of language modeling?**

According to Section 3.6 of the J&M textbook, here are the primary challenges that language models like KenLM aim to tackle:
* **KenLM focuses on efficient storage and retrieval of n-grams to minimize memory and processing requirement.** It uses memory-efficient representations of language models such as 64-bit hash numbers for words and quantized probabilities to reduce storage space.
* **KenLM prunes less important n-gram.** It uses sorted arrays and efficiently combine probabilities and backoffs in a single value. It uses merge sorts to efficiently build the probability tables in a minimal
number of passes through a large corpus.

### Differences Between Your Implementation and KenLM
Examine and outline the key distinctions between your own implementation (developed in this assignment) and KenLM. What sets your approach apart from KenLM in terms of methodology, algorithms, data structures, or implementation strategies? You can answer this question from the perspective of one or more of the following: space and time complexity, accuracy, biases, portability.

* **Space and time complexity:** My models have a maximum space and time complexity of O(n^3). My trigram model is stored as a dictionary of dictionary of dictionary, and each "layer", representing a dimension has a space complexity of O(n), and looping variables inside the model has a time complexity of O(n^3). My unigram and bigram models should have a smaller space and time complexity. As for KenLM, as mentioned in the first question, their design should have a much smaller space and time complexity given the used a more efficient design to implement their models.
* **Accuracy and bias:** Given the perplexities my models gives vs perplexities KenLM trained models give, I believe there is not much accuracy and bias differences training this size of dataset. Maybe the discrepancy will get larger as the dataset is larger or N gets larger, and KenLM will perform better, given it is designed to train large language model.
* **Portability:** KenLM is more portable and efficient for large-scale n-gram models due to optimized storage and retrieval, while Python-based models may be more accessible but less efficient and scalable.