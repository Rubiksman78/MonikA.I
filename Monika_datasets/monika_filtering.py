#%%
import re
import os
import itertools

def modify_text(path,dest_path):
    with open(path, "r",encoding="utf-8") as f:
        lines = f.readlines()
    #removes spaces at the beginning and end of the string
    lines = [line.strip() for line in lines]

    #remove # before the lines
    lines = [line[1:] for line in lines if line.startswith("#")] + [line for line in lines if not line.startswith("#")]
    #keep lines beginning with "m "
    lines = [line for line in lines if line.startswith("m ")]
    #print(len(lines))

    #remove " from the sentences
    lines = [line.replace('"', "") for line in lines] 
    # #split each line into a list of words
    lines = [line.split(" ") for line in lines]
    #print(lines[:10])

    #remove the firt=st 2 words of each lines if the second word begins with a digit
    lines = [line[2:] for line in lines if line[1].startswith("0") or line[1].startswith("1") or line[1].startswith("2") or line[1].startswith("3") or line[1].startswith("4") or line[1].startswith("5") or line[1].startswith("6") or line[1].startswith("7") or line[1].startswith("8") or line[1].startswith("9")] + [line[1:] for line in lines if not (line[1].startswith("0") or line[1].startswith("1") or line[1].startswith("2") or line[1].startswith("3") or line[1].startswith("4") or line[1].startswith("5") or line[1].startswith("6") or line[1].startswith("7") or line[1].startswith("8") or line[1].startswith("9"))]

    #join the words back into a string
    lines = [" ".join(line) for line in lines]

    lines = [line.replace("abcd", "") for line in lines]
    #remove sentences with less than 2 words
    lines = [line for line in lines if len(line.split(" ")) > 2]

    #remove characters in {} and [] and ()
    lines = [re.sub(r"\[.*?\]", "Sam-chan", line) for line in lines]
    lines = [re.sub(r"\{.*?\}", "", line) for line in lines]
    lines = [re.sub(r"\(.*?\)", "", line) for line in lines]

    #remove words longer than 50 characters
    lines = [re.sub(r"\w{50,}", "", line) for line in lines]
    #remove punctuation
    #lines = [re.sub(r"[^\w\s]", "", line) for line in lines]
    #add space between punctuation and words
    lines = [re.sub(r"([?.!,])", r" \1 ", line) for line in lines]
    #remove ~
    lines = [re.sub(r"~", "", line) for line in lines]

    #replace ’ and ‘ with '
    lines = [re.sub(r"’", "'", line) for line in lines]
    lines = [re.sub(r"‘", "'", line) for line in lines]
    #replace numbers with #s
    #lines = [re.sub(r"\d", "#", line) for line in lines]

    #remove contractions
    
    lines = [re.sub(r"'s", " is", line) for line in lines]
    lines = [re.sub(r"'m", " am", line) for line in lines]
    lines = [re.sub(r"'re", " are", line) for line in lines]
    lines = [re.sub(r"'ll", " will", line) for line in lines]
    lines = [re.sub(r"'ve", " have", line) for line in lines]
    lines = [re.sub(r"'d", " would", line) for line in lines]

    #remove same lines
    lines = list(dict.fromkeys(lines))

    #group . . .
    #remove extra spaces
    #lines = [re.sub(r"\s+", " ", line) for line in lines]

    #remove unrecognized characters
    #lines = [re.sub(r"[^a-zA-Z0-9\s]", "", line) for line in lines]

    #remove spaces > 1
    lines = [re.sub(r"\s{2,}", " ", line) for line in lines]    
    #Write the lines to a new file
    with open(dest_path, "w") as f:
        for line in lines:
            try:
                f.write(line + "\n")
            except:
                pass

def combine_filtered(path, dest_path):
    files = os.listdir(path)
    files = [file for file in files if file.endswith("_filtered.txt")]
    with open(dest_path, "w",encoding="utf-8") as f:
        for file in files:
            with open(path + "/" + file, "r") as f2:
                lines = f2.readlines()
            for line in lines:
                f.write(line)

if __name__ == "__main__":
    #Filter all text files beginning with the expression "script"
    #List files in the directory
    files = os.listdir("./")
    #Filter files
    files = [file for file in files if file.startswith("script")]
    #Filter files with .txt extension
    files = [file for file in files if file.endswith(".txt") and not file.endswith("_filtered.txt")]
    for file in files:
        modify_text(file, file.replace(".txt", "_filtered.txt"))
    combine_filtered("./", "monika_dataset.txt")
    #Print max sentence length
    with open("monika_dataset.txt", "r",encoding="utf8") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lengths = [len(line.split(" ")) for line in lines]
    print(max(lengths))

    #print word count appearance
    words = [line.split(" ") for line in lines]
    words = list(itertools.chain.from_iterable(words))
    words = [word.lower() for word in words]
    #count words
    word_count = {}
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    #sort words by count
    word_count = {k: v for k, v in sorted(word_count.items(), key=lambda item: item[1], reverse=True)}
    #print first 100 words
    print(list(word_count.items())[:1000])