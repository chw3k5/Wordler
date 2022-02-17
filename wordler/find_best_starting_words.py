import numpy as np
import matplotlib.pyplot as plt

from narrow import *

rerun = False #takes a long time

av = AvailableWords()

all_outcomes_list = []
for i in range(0,3): #sorry for my for loop
    for j in range(0,3):
        for k in range(0,3):
            for n in range(0,3):
                for m in range(0,3):
                    all_outcomes_list.append(str(i)+str(j)+str(k)+str(n)+str(m))

print(len(all_outcomes_list))


# there are a lot of cases where the outcome is impossible should I average or total or minimize
# it seems given every possible outcome every word is possible.
# sum is always 2315 so not useful
# want sum of length*likelyhood = sum(length(all_outcomes)*(len(all_outcomes)/total_possible_words)
# should equal average list length 
if rerun:
    remaining_words_given_outcome = np.zeros((len(all_outcomes_list),len(av.all_word_list)))
    for k in range(0,len(av.all_word_list)):
        guess_word = av.all_word_list[k]
        print(k,guess_word)
        for i in range(0,len(all_outcomes_list)):
            av = AvailableWords()
            av.ask_guess(guess_word =guess_word,results = all_outcomes_list[i] )
            remaining_words_given_outcome[i,k] = len(av.remaining_words)
        print(np.max(remaining_words_given_outcome[:,k]))
    np.save("result.npy",remaining_words_given_outcome)
else:
    remaining_words_given_outcome = np.load("result.npy")


average_remaining_list_length = np.sum(remaining_words_given_outcome*remaining_words_given_outcome/len(av.all_word_list),axis = 0)
a = np.argsort(average_remaining_list_length)
sorted_words = np.asarray(av.all_word_list)[a]
sorted_values = average_remaining_list_length[a]

print("word| likely length of narrowed list")
for i in range(0,20):
    print(sorted_words[i],sorted_values[i])
    
