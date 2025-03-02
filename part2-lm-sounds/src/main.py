# This program should loop over the files listed in the input file directory,
# assign perplexity with each language model,
# and produce the output as described in the assignment description.
from collections import Counter
import math, sys

OOV_THRESHHOLD = 30

TRAINING_SET = "data/training.txt"
DEV_SET = "data/dev.txt"
    
class Unigram:
    '''
    This class trains a unigram with the given training set.
    '''
    def __init__(self, training_set: str):
        # counts is a table that stores the counts of each token
        # total is the total number of tokens
        # model is the table that stores the probability of each token
        self.counts, self.total, self.model = self.process_dataset(training_set)

    def process_dataset(self, dataset: str) -> (Counter, int, dict):
        '''
        This method takes in the path to the dataset, process it and return a count table,
        total count and a probability table.
        '''
        # Read in file
        with open(dataset, "r") as file:
            data = file.readlines()
        all_tokens = list()
        for line in data:
            tokens = line.split(" ")
            for token in tokens:
                if token != "\n":
                    all_tokens.append(token)
    
        # OOV Handling (see README.md)
        global OOV_THRESHHOLD
        counts = Counter(all_tokens)
        counts = ['<UNK>' if counts[token] <= OOV_THRESHHOLD else token for token in all_tokens]

        # Train model
        counts = Counter(counts)
        total = sum(counts.values())
        model = {}
        for item, count in counts.items():
            percentage = (count / total)
            model[item] = percentage
        
        return counts, total, model

    def token_probability(self, token: str) -> float:
        '''
        This method takes in a token and returns the probability of it.
        '''
        # Treat unseen tokens as <UNK>
        if token not in self.model.keys():
            token = "<UNK>"

        return self.model[token]
    
    def token_count(self, token: str):
        '''
        This method takes in a token and returns the count of it.
        '''
        # Treat unseen tokens as <UNK>
        if token not in self.model.keys():
            token = "<UNK>"

        return self.model[token] * self.total

    def perplexity(self, dataset: str = "training") -> float:
        '''
        This method calculates and return the perplexity of the model or dev set, 
        indicated in the parameter dataset.
        '''
        # Perplexity of the training set
        if dataset == "training":
            log_prob_sum = sum(
                -math.log(self.token_probability(token)) * count
                for token, count in self.counts.items()
            )
            perplexity = math.exp(log_prob_sum / self.total)

        # Perplexity of the dev set
        else:
            dev_counts, dev_total, _ = self.process_dataset(dataset)
            for key, count in dev_counts.items():
                if key not in self.counts:
                    dev_counts["<UNK>"] += count
                    del dev_counts[key]  
            log_prob_sum = sum(
                -math.log(self.token_probability(token)) * count
                for token, count in dev_counts.items()
            )
            perplexity = math.exp(log_prob_sum / dev_total)
            
        return perplexity

class Bigram:
    '''
    This class trains a bigram with the given training set.
    '''
    def __init__(self, training_set, smoothing=False):
        # model is the count table
        # total_count is the total count of the whole table
        # all_tokens stores a list of all tokens in the dataset
        self.smoothing = smoothing
        self.model, self.total_count, self.all_tokens = self.process_dataset(training_set, smoothing)
        self.unigram = Counter(self.all_tokens) # Create a unigram for perplexity calculations
        
    def oov_process(self, dataset):
        '''
        This function determines which tokens are to be changed into <UNK> with a given oov threshhold,
        and return (1) a set of tokens that are kept unchanged and (2) a set of tokens that has been
        changed to <UNK>
        '''
        with open(dataset, "r") as file:
            data = file.readlines()
        
        # Creates a list of all tokens
        all_tokens = list()
        for line in data:
            tokens = line.split(" ")
            for token in tokens:
                if token != "\n":
                    all_tokens.append(token)
        
        # OOV handling
        global OOV_THRESHHOLD
        counts = Counter(all_tokens)

        # Count tokens and seperate into two lists: tokens with count >= 30 or otherwise
        tokens_changed_to_unk = set([token for token in all_tokens if counts[token] <= OOV_THRESHHOLD])
        needed_tokens = set([token for token in all_tokens if counts[token] > OOV_THRESHHOLD])
        needed_tokens.add("<UNK>")
        counts = ['<UNK>' if counts[token] <= OOV_THRESHHOLD else token for token in all_tokens] 
        counts = Counter(counts)

        return needed_tokens, tokens_changed_to_unk

    def process_dataset(self, training_set, smoothing):
        '''
        This method takes in the path to the dataset, process it and return model (a count table),
        total_count and a list of all tokens.
        '''
        # Calls self.oov_process() to handle OOV
        needed_tokens, changed_tokens = self.oov_process(dataset=training_set)

        # rows is the given event, columns is the event of interest
        rows = list(needed_tokens).copy()
        rows.append("<s>")
        rows.append("</s>")
        columns = list(needed_tokens).copy()
        columns.append("<s>")
        columns.append("</s>")

        # Initialize model
        if smoothing:
            model = {row: {col: 1 for col in columns} for row in rows}
        else:
            model = {row: {col: 0 for col in columns} for row in rows}

        # Read in training set and count 
        with open(TRAINING_SET, "r") as file:
            data = file.readlines()
        
        # Insert begin-of-utterance and end-of-utterance tokens
        all_tokens = list()
        for line in data:
            tokens = line.split(" ")[:-1]
            tokens.insert(0, "<s>")
            tokens.append("</s>")
            tokens = ["<UNK>" if item in changed_tokens else item for item in tokens]

            # Save all tokens
            for token in tokens:
                all_tokens.append(token)

            # Logging count
            for i in range(len(tokens) - 1):
                given = tokens[i]
                interest = tokens[i + 1]
                model[given][interest] += 1
        
        # Calculates total count of the whole table
        total_count = 0
        for row in rows:
            for col in columns:
                total_count += model[row][col]

        return model, total_count, all_tokens

    def token_count(self, interest, given) -> int:
        '''
        This method returns the count of the word of interest given its previous word.
        '''
        # Treat unseen tokens as <UNK>
        if given not in self.model:
            given = "<UNK>"
        if interest not in self.model[given]:
            interest = "<UNK>"

        return self.model[given][interest]
    
    def unigram_count(self, interest) -> int:
        '''
        This method returns the unigram count of the word of interest.
        '''
        # Treat unseen tokens as <UNK>
        if interest not in self.unigram:
            interest = "<UNK>"

        return self.unigram[interest]

    def perplexity(self, dataset: str = "training") -> float:
        '''
        This method calculates and return the perplexity of the model or dev set, 
        indicated in the parameter dataset.
        '''
        if dataset == "training":
            # Sum up log probabilities
            log_prob_sum = 0
            for given in self.model:
                for interest in self.model[given]:
                    count_wiMinus1_wi = self.token_count(interest, given)
                    count_w = self.unigram[given]
                    if count_wiMinus1_wi != 0 and count_w != 0:
                        probability_wi_give_wiMinus1 = count_wiMinus1_wi / count_w
                        log_prob_sum += math.log(probability_wi_give_wiMinus1) * count_wiMinus1_wi

            # Calculate perplexity
            perplexity = math.exp((-1 / self.total_count) * log_prob_sum)

            return perplexity
                             
        else:
            dev_model, dev_count, _ = self.process_dataset(dataset, self.smoothing)
            # Sum up log probabilities
            log_prob_sum = 0
            for given in dev_model:
                for interest in dev_model[given]:      
                    count_wiMinus1_wi = self.token_count(interest, given)
                    count_w = self.unigram_count(given)
                    if count_wiMinus1_wi != 0 and count_w != 0:
                        probability_wi_give_wiMinus1 = count_wiMinus1_wi / count_w
                        log_prob_sum += math.log(probability_wi_give_wiMinus1) * count_wiMinus1_wi
            # Calculate perplexity        
            perplexity = math.exp((-1 / dev_count) * log_prob_sum)

            return perplexity

class Trigram:
    '''
    This class trains a trigram with the given training set.
    '''
    def __init__(self, training_set, smoothing=False):
        self.smoothing = smoothing
        # Bigram model and Trigram model and their respective total counts
        (
            self.bigram_model, 
            self.bigram_total_count, 
            self.trigram_model, 
            self.trigram_total_count, 
            self.all_tokens
        ) = self.process_dataset(training_set, smoothing)
        # Unigram of this dataset
        self.unigram = Counter(self.all_tokens)

    def oov_process(self, dataset):
        '''
        This function determines which tokens are to be changed into <UNK> with a given oov threshhold,
        and return (1) a set of tokens that are kept unchanged and (2) a set of tokens that has been
        changed to <UNK>
        '''
        # Read in file
        with open(dataset, "r") as file:
            data = file.readlines()

        # Store all tokens
        all_tokens = list()
        for line in data:
            tokens = line.split(" ")
            for token in tokens:
                if token != "\n":
                    all_tokens.append(token)

        # OOV handling
        global OOV_THRESHHOLD
        counts = Counter(all_tokens)

        # Split tokens into two lists: tokens with count >= 30 and otherwise
        tokens_changed_to_unk = set([token for token in all_tokens if counts[token] <= OOV_THRESHHOLD])
        needed_tokens = set([token for token in all_tokens if counts[token] > OOV_THRESHHOLD])
        needed_tokens.add("<UNK>")
        counts = ['<UNK>' if counts[token] <= OOV_THRESHHOLD else token for token in all_tokens] 
        counts = Counter(counts)

        return needed_tokens, tokens_changed_to_unk

    def process_dataset(self, dataset, smoothing):
        '''
        This method takes in the path to the dataset, process it and returns: 
        (1) bigram model
        (2) total count of the bigram model
        (3) trigram model 
        (4) total count of the trigram model
        (5) all tokens in the given dataset
        '''
        needed_tokens, changed_tokens = self.oov_process(dataset)

        # Bigram Model
        dimension = list(needed_tokens).copy()
        dimension.append("<s>")
        dimension.append("</s>")
        rows = dimension.copy()
        columns = dimension.copy()
        depth = dimension.copy()

        # Initialize bigram model
        if smoothing:
            bigram_model = {row: {col: 1 for col in columns} for row in rows}
        else:
            bigram_model = {row: {col: 0 for col in columns} for row in rows}

        with open(TRAINING_SET, "r") as file:
            data = file.readlines()
        
        # Use these tokens to train unigram
        all_tokens = list()

        # Insert 1 begin-of-utterance tokens and 1 end-of-utterance
        for line in data:
            tokens = line.split(" ")[:-1]
            tokens.insert(0, "<s>")
            tokens.insert(0, "<s>")
            tokens.append("</s>")
            tokens = ["<UNK>" if item in changed_tokens else item for item in tokens]

            # Store all tokens
            for token in tokens:
                all_tokens.append(token)

            # Log counts into table
            for i in range(len(tokens) - 1):
                given = tokens[i]
                interest = tokens[i + 1]
                bigram_model[given][interest] += 1
        
        # Calculates bigram total count
        bigram_total_count = 0
        for row in rows:
            for col in columns:
                bigram_total_count += bigram_model[row][col]

        # Initialize trigram model
        if smoothing:
            trigram_model = {row: {col: {dep: 1 for dep in depth} for col in columns} for row in rows}
        else:
            trigram_model = {row: {col: {dep: 0 for dep in depth} for col in columns} for row in rows}

        with open(TRAINING_SET, "r") as file:
            data = file.readlines()

        # Insert 2 begin-of-utterance tokens and 1 end-of-utterance
        for line in data:
            tokens = line.split(" ")[:-1]
            tokens.insert(0, "<s>")
            tokens.insert(0, "<s>")
            tokens.append("</s>")
            tokens = ["<UNK>" if item in changed_tokens else item for item in tokens]

            # Log counts into table
            for i in range(len(tokens) - 2):
                given = tokens[i]
                given2 = tokens[i + 1]
                interest = tokens[i + 2]
                trigram_model[given][given2][interest] += 1

        # Calculates trigram total count
        trigram_total_count = 0
        for row in rows:
            for col in columns:
                for dep in depth:
                    trigram_total_count += trigram_model[row][col][dep]
 
        return bigram_model, bigram_total_count, trigram_model, trigram_total_count, all_tokens
        
    def bigram_token_count(self, interest, given):
        '''
        This method returns the bigram count of the word of interest given its previous word.
        '''
        return self.bigram_model[given][interest]
    
    def trigram_token_count(self, interest, given1, given2):
        '''
        This method returns the trigram count of the word of interest given its 2 previous words.
        Example: eat an apple
        given1 = "eat", given2 = "an", word of interest = "apple"
        '''
        return self.trigram_model[given1][given2][interest]
    
    def perplexity(self, dataset: str = "training"):
        '''
        This method calculates and return the perplexity of the model or dev set, 
        indicated in the parameter dataset.
        '''
        if dataset == "training":
            # Sum up log probabilities
            log_prob_sum = 0
            for given1 in self.trigram_model:
                for given2 in self.trigram_model[given1]:
                    for interest in self.trigram_model[given1][given2]:
                        trigram_count = self.trigram_token_count(interest, given1, given2)               
                        bigram_count = self.bigram_token_count(given2, given1)
                        if trigram_count != 0 and bigram_count != 0:
                            probability = trigram_count / bigram_count
                            log_prob_sum += math.log(probability) * trigram_count

            # Calculate perplexity
            perplexity = math.exp((-1 / self.trigram_total_count) * log_prob_sum)

            return perplexity
                        
        else:
            _, _, dev_trigram_model, dev_trigram_total_count, _ = self.process_dataset(dataset, self.smoothing)
            # Sum up log probabilities
            log_prob_sum = 0
            for given1 in dev_trigram_model:
                for given2 in dev_trigram_model[given1]:
                    for interest in dev_trigram_model[given1][given2]:
                        trigram_count = self.trigram_token_count(interest, given1, given2)               
                        bigram_count = self.bigram_token_count(given2, given1)
                        if trigram_count != 0 and bigram_count != 0:
                            probability = trigram_count / bigram_count
                            log_prob_sum += math.log(probability) * trigram_count

            # Calculate perplexity
            perplexity = math.exp((-1 / dev_trigram_total_count) * log_prob_sum)

            return perplexity

def main():
    '''
    Reads in arguments passed into main.py and train and evaluate the required model.
    '''
    try:
        if len(sys.argv) >= 4: 
            global TRAINING_SET
            global DEV_SET

            n_gram_type = sys.argv[1]      # unigram, bigram, or trigram
            TRAINING_SET = sys.argv[2]     # path to the training set
            DEV_SET = sys.argv[3]          # path to the dev set (the set to be calculate PPL on)
            smoothing = False              # default = False if no --laplace is passed in
        
        if len(sys.argv) == 5:
            if sys.argv[4] == "--laplace": # set smoothing True if --laplace is passed in
                smoothing = True

    except:
        error_message = "Please check README.md for example usage"
        raise KeyError(error_message)
    
    # Train n gram model given its type
    if n_gram_type == "unigram":
        model = Unigram(TRAINING_SET)
    
    elif n_gram_type == "bigram":
        model = Bigram(TRAINING_SET, smoothing)
    
    elif n_gram_type == "trigram":
        model = Trigram(TRAINING_SET, smoothing)

    # Evaluate model with the perplexity metric
    dev_set_perplexity = model.perplexity(DEV_SET)
    
    # Print out statistics
    print("N-gram type: " + n_gram_type.title())
    if smoothing:
        print("Smoothing: " + "Laplace")
    else:
        print("Smoothing: None")
    print("Perplexity: " + str(round(dev_set_perplexity, 5)))

if __name__ == "__main__":
    main()