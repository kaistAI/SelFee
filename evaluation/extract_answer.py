# # # Open the file for reading
# with open('log_file2.txt', 'r') as f:

#     # Initialize lists to store the numbers
#     list1 = []
#     list2 = []
#     list3= []
#     chatwin=0
#     equal=0
#     win =0

#     # Loop through each line of the file
#     for line in f:

#         # Check if the line contains "INFO:__main__:"
#         if "INFO:__main__:" in line:

#             # Extract the numbers after "INFO:__main__:"
#             numbers = line.split(":")[2].split()

#             # Convert the numbers to floats and append to the appropriate list
#             if len(numbers) == 2:
#                 # Convert the numbers to floats and append to the appropriate list
#                 if numbers[0] > numbers[1]:
#                     chatwin+=1
#                 elif numbers[0] == numbers[1]:
#                     equal+=1
#                 else: 
#                     win +=1
#                 list1.append(float(numbers[0]))
#                 list2.append(float(numbers[1]))


#     # Calculate the average of the two lists of numbers
#     print(sum(list1))
#     print(sum(list2))
#     print(chatwin, equal, win)
#     # avg_list = [(a + b) / 2 for a, b in zip(list1, list2)]

#     # Print the average list
#     # print(avg_list)

import jsonlines

# Open the file for reading
# with open('vicuna-7b_20230322-fp16/review_gpt35_vicuna-7b.jsonl', 'r') as f:

first_won=0
equal=0
first_lose=0
index=0

# open the JSONL file for reading
with jsonlines.open('selfee_13b_singleturn_revision3_reverse_guanaco.jsonl', 'r') as reader:
# with jsonlines.open('unicorn_flan_alpaca_merged/review_unicorn_flan_alpaca_merged_chatgpt_reverse.jsonl', 'r') as reader:

    # initialize the sums for each index of the score list
    sum_index_0 = 0
    sum_index_1 = 0


    # iterate over each row in the JSONL file
    for row in reader:
        index +=1

        # extract the score field from the row
        score = row['score']



        # add the values at index 0 and index 1 to their respective sums
        sum_index_0 += score[0]
        sum_index_1 += score[1]



        if score[0] > score[1]:
            first_won += 1
        elif score[0] == score[1]:
            equal +=1
        elif score[0] < score[1]:
            first_lose += 1
    

    # print the sums
    print("Sum of index 0:", sum_index_0)
    print("Sum of index 1:", sum_index_1)
    print("Win rate", first_won, equal, first_lose)