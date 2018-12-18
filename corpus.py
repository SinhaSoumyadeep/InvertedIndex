import os
import re
import json
import sys
import nltk
from more_itertools import locate
from prettytable import PrettyTable


from bs4 import BeautifulSoup

#This is the path where the raw HTML corpus was downloaded in Assignment 1
directory = "../../Assignment1/files/DownloadHTML/['Carbon_footprint']"

#This is the Path where the cleaned corpus is stored as a text file.
savePath = "../savedFiles"

#This is the data structure to store index with term location for unigram.
index_having_term_locations = {}

#This is the data Structure for inverted Index.
inverted_index = {}

#This is a dictionary to store the number of terms per document.
terms_per_document = {}

#This is a dictionary to store the length of the index list for terms.
term_with_length_of_index_list = {}

#This is the stop index or the cut off value.
stopIndex = 7

#this flag is set to true if punctuation Handling is required.
punctuationHandlingFlag = False
#this flag is set to true if casefolding is required.
caseFoldingFlag = False

#this is the threshold for term frequency for generating stop list
tf_threshold = 400#bigram: 2500 #unigram: 7000

#this is the threshold for document frequency for generating stop list
df_threshold = 250#bigram: 450 #unigram: 700






#This function is used to filter out keywords from the soup object.
def filter(soup, tag):
    for content in soup.find_all(tag):
        content.extract()
    return soup

#This function is used to fetch the filename by splitting the url.
def getfilename(path):
    fileurl = str(path).split("/")
    filename = fileurl[fileurl.__len__() - 1]
    return  filename



#This function is used to filter out urls with ":".
def checkForColon(link):
    p = re.compile("https://en.wikipedia.org/wiki/(.)*:(.)*")
    m = p.match(link)
    if m:
        return True
    else:
        return False




#This function is used to crawl the raw html corpus.
def extractFiles(file):

    global caseFoldingFlag
    global punctuationHandlingFlag

    print("*********** crawling file "+file+" *****************")

    filtertag = ["table", "img"]

    try:
        fileContent = open(directory+"/"+file, "r", encoding="utf-8")

    except:
        print(file+" file doesnot exist!")
        return
    soup = BeautifulSoup(fileContent.read(), 'html.parser')

    file_title = soup.title.string.strip().replace(' - Wikipedia', '')  # Extracting and storing the title as string

    soup = extractbodytag(soup)

    for tag in filtertag:
        soup = filter(soup, tag)

    soupText = file_title+"\n"+cleanMe(soup)

    if(caseFoldingFlag == True):
        soupText = handle_case_folding(soupText)

    if(punctuationHandlingFlag == True):
        soupText = handle_punctuation(soupText)

    if not os.path.exists(savePath):
        os.mkdir(savePath)

    f = open(savePath+"/"+file, "w",encoding='utf-8')
    f.write(soupText)
    f.close()

#This method is used to clean up the raw html corpus.
def cleanMe(soup):

    for page_content in soup.find_all('div', {'id': ["mw-content-text"]}):
       soup = page_content.extract()
    for script in soup(["script", "style","table","img","math","sup","ol","li","ul"]):
        script.extract()

    for page_content in soup.find_all('div', {'id': ['toc', 'mw-hidden-catlinks']}):
        page_content.extract()

    for page_content in soup.find_all('a', {'rel': ['nofollow']}):
        page_content.extract()
    for edit_section in soup.find_all('span', {'class': ['mw-editsection', 'nowrap']}):
        edit_section.extract()
    text = soup.get_text()

    text = text.replace("\\n","@newline@")
    text = text.replace("\\t", "@tabs@")

    text = re.sub("(@newline@)+","\n",text)

    text = re.sub("(@tabs@)+", "", text)
    text = re.sub("(\n)+", "\n", text)

    return text

#This method is to remove the punctuations from The texts and numbers found in clean Corpus.
def handle_punctuation(soupText):
    cleanUpPunctuation = ""
    punctuationRemovalListForText =['!','@','#','$','%','^','&','*','(', ')','+','_','=','{','}','[',']',':',';','"','|','\\\'',',','<',  '>','.','/','?','`','“', '”','☇', '′', '～','☉','~','，', '、', '⹁']
    punctuationRemovalListForNumber = ['!','@','#','&','(', ')','[',']','{','}','“', '”','?','\'','"',';','_', '`', '☉','|',  '~', '′', '～', '、', '⹁', '☇' ]

    htmlTextFile = soupText.split()
    for terms in htmlTextFile:
        if bool(re.search(r'\d', terms)):
            for punctuations in punctuationRemovalListForNumber:
                terms = terms.replace(punctuations, '')
            cleanUpPunctuation = cleanUpPunctuation + ' ' + terms

        else:
            for punctuations in punctuationRemovalListForText:
                terms = terms.replace(punctuations, '')

            cleanUpPunctuation = cleanUpPunctuation + ' ' + terms

    return cleanUpPunctuation

#This method is used to handle case folding.
def handle_case_folding(soupText):
    return soupText.lower()

#This function is used to extract the Body of the Html page.
def extractbodytag(soup):
    for content in soup.find_all("body"):
        soup = content.extract()
    return soup

#this method is used to get all the raw html corpus files in the dictory specified.
def getTheFiles():

    global punctuationHandlingFlag
    global caseFoldingFlag



    answerForPunctuation = input(" do you want the punctuations to be handled? (y/n)")

    if(str(answerForPunctuation).lower() == 'y'):
       punctuationHandlingFlag = True

    answerForCaseFolding = input(" do you want case-folding? (y/n)")
    if (str(answerForCaseFolding).lower() == 'y'):
       caseFoldingFlag = True




    for file in files(directory):
       if file.startswith("."):
           continue
       else:
           extractFiles(file)

#This is to get the list of files in the directory mentioned.
def files(path):
   for file in os.listdir(path):
       if os.path.isfile(os.path.join(path, file)):
           yield file

#This is a method to write a JSON file.
def writeJson(filename, dict):
    if not os.path.exists("../jsonFiles"):
        os.mkdir("../jsonFiles")

    f = open("../jsonFiles/"+filename+"JSON.json", "w")
    convertedJson = json.dumps(dict)
    f.write(convertedJson)
    f.close()

#This is to calculate the dGaps.
def dgaps(lst):
    dgap = []
    dgap.append(lst[0])
    diff = 0;
    for i in range(len(lst) - 1):
        # adding the alternate numbers
        diff = lst[i + 1] - lst[i]
        dgap.append(diff)

    return dgap

#This method is used to generate an inverted index with term location.
def build_inverted_index_with_term_location(terms_in_clean_file, file):
    for term in terms_in_clean_file:
        count = 0
        dgap = dgaps(list(locate(terms_in_clean_file, lambda x: x == term)))
        if term not in index_having_term_locations:
            index_having_term_locations[term] = [[file, dgap]]
        else:
            for i in range(len(index_having_term_locations[term])):
                if index_having_term_locations[term][i][0] == file:
                    break
                else:
                    count = count + 1
            if count == len(index_having_term_locations[term]):
                index_having_term_locations[term].append([file, dgap])


#this method is used to generate inverted index list.
def build_inverted_index(terms_in_clean_file,file):

    for term in terms_in_clean_file:
        term = str(term)
        length = 0
        if term not in inverted_index:
            inverted_index[term] = [[file, 1]]
        else:
            for i in range(len(inverted_index[term])):
                if inverted_index[term][i][0] == file:
                    inverted_index[term][i][1] = inverted_index[term][i][1] + 1
                else:
                    length = length + 1
            if length == len(inverted_index[term]):
                inverted_index[term].append([file, 1])


        terms_per_document[file] = len(set(terms_in_clean_file))



#This is a method to generate the ngrams based on the parameter passed.
def readFile(file, ngram):
    try:
        fileContent = open(savePath+"/"+file, "r", encoding="utf-8")

    except:
        print(file+" file doesnot exist!")
        return

    textFile = fileContent.read()

    #unigram
    if ngram == "unigram":
        terms_in_clean_file = str(textFile).split()


    #bigram
    if ngram == "bigram":
        terms_in_clean_file = str(textFile).split()
        terms_in_clean_file = list(nltk.bigrams(terms_in_clean_file))

    #trigtram
    if ngram == "trigram":
        terms_in_clean_file = str(textFile).split()
        terms_in_clean_file = list(nltk.trigrams(terms_in_clean_file))

    if ngram == "unigram":
        build_inverted_index_with_term_location(terms_in_clean_file, file)

    build_inverted_index(terms_in_clean_file,file)


#This is the method to get terms with length of index list.
def getTermsWithLengthOfIndexList(ngram):
    for keys in inverted_index:
        term_with_length_of_index_list[keys] = len(inverted_index[keys]);

    writeJson(ngram+"_list_of_terms_with_index_list_length",term_with_length_of_index_list)

#This method is used to reload the Inverted Index json file.
def loadInvertedIndex(ngram):
    global inverted_index
    inverted_index.clear()
    with open("../jsonFiles/" + ngram + "_inverted_indexJSON.json") as f:
        inverted_index = json.load(f)

#This method is used to create a stop list.
def writeStopList(stopList, termDocIdTable, ngram):


    #print(termDocIdTable)
    f = open("../jsonFiles/stopList_" + ngram + ".txt", "w")

    for list in stopList:
        if list[1] > tf_threshold and len(termDocIdTable[list[0]])>df_threshold:
            f.write(list[0]+"\n")

    f.close()





    # f = open("../jsonFiles/stopList_" + ngram + ".txt", "w")
    # for stopElement in stopList[:stopIndex]:
    #     f.write(stopElement[0]+" : "+str(stopElement[1])+"\n")
    #
    # f.close()

#This method is used to write a table.
def writeTable(termDocIdTable, ngram):
    f = open("../jsonFiles/" + ngram + '_df_table.txt', 'w', encoding='utf-8')
    for key in sorted(termDocIdTable.keys()):
        f.write(key+" : "+strumString(termDocIdTable[key])+" : "+str(len(termDocIdTable[key]))+"\n")

    f.close()

#This method is used to build sorted term frequency table.
def buildSortedTermFrequencyTable(ngram):
    loadInvertedIndex(ngram)
    termFrequenctTable = {}
    termDocIdTable = {}

    for keys in inverted_index.keys():
        sum = 0
        docIdlist = set()
        for list in inverted_index[keys]:
            sum = sum+list[1]
            docIdlist.add(list[0])

        termFrequenctTable[keys] = sum
        termDocIdTable[keys] = docIdlist

    sortedTermFrequenctTable = sorted(termFrequenctTable.items(), key=lambda kv: kv[1], reverse=True)
    tf_table = PrettyTable(['term', 'term_frequency'])
    for elements in sortedTermFrequenctTable:
        tf_table.add_row([elements[0], elements[1]])
    with open("../jsonFiles/" + ngram + '_tf_table.txt', 'w', encoding='utf-8') as f:
        f.write(str(tf_table))

    writeStopList(sortedTermFrequenctTable, termDocIdTable, ngram)

    writeTable(termDocIdTable, ngram)


#This method is used to create a string separated by comma.
def strumString(list):
    str = ""
    for string in list:

        str = str+string+", "

    return str[:-2]

#This method is used to help build the inverted index, terms per document and invertedindex with term positions.
def getCleanCorpus(ngram):
    fileList = os.listdir(savePath)

    if(ngram == "unigram"):
        print("building unigram")
        for file in fileList:
            if file.startswith("."):
                continue
            else:
                print(file)
                readFile(file, "unigram")

        getTermsWithLengthOfIndexList("unigram")
        writeJson("unigram_inverted_index",inverted_index)
        writeJson("unigram_term_perdoc", terms_per_document)
        writeJson("unigram_inverted_index_with_term_positions", index_having_term_locations)

        index_having_term_locations.clear()
        inverted_index.clear()
        terms_per_document.clear()
        term_with_length_of_index_list.clear()

    if (ngram == "bigram"):
        print("building bigram")
        for file in fileList:
            if file.startswith("."):
                continue
            else:
                print(file)
                readFile(file, "bigram")

        getTermsWithLengthOfIndexList("bigram")
        writeJson("bigram_inverted_index",inverted_index)
        writeJson("bigram_term_perdoc", terms_per_document)


        inverted_index.clear()
        terms_per_document.clear()
        term_with_length_of_index_list.clear()

    if (ngram == "trigram"):
        print("building trigram")
        for file in fileList:
            if file.startswith("."):
                continue
            else:
                print(file)
                readFile(file, "trigram")

        getTermsWithLengthOfIndexList("trigram")
        writeJson("trigram_inverted_index",inverted_index)
        writeJson("trigram_term_perdoc", terms_per_document)

#This is method to decode the dGaps.
def dGapsDecoder(list):

    decodedPositions = []
    currentPos = list[0];
    decodedPositions.append(currentPos)
    for position in list[1:]:
        currentPos = currentPos+position
        decodedPositions.append(currentPos)

    return decodedPositions

#This method is used to find the proximity of the words.
def findAdjecency(positionOfList1, positionOfList2, proximityWindow):

    terms_are_in_proximity = False
    for pos in positionOfList1:
        for p in positionOfList2:
            if abs(pos - p) <= proximityWindow:
                terms_are_in_proximity = True
                break

    return terms_are_in_proximity


#This method is used to generate a list of document with terms which are in proximity within k terms.
def task3(term1, term2, proximityWindow):
    global index_having_term_locations

    index_having_term_locations.clear()



    with open("../jsonFiles/unigram_inverted_index_with_term_positionsJSON.json") as f:
        index_having_term_locations = json.load(f)

    f = open("../jsonFiles/" + term1 + "_" + term2 + "_proximity_with_proximityWindow_" + str(proximityWindow) + '.txt',
             'w', encoding='utf-8')

    for listOfDocs1 in index_having_term_locations[term1]:
        for listOfDocs2 in index_having_term_locations[term2]:
            if(listOfDocs1[0] == listOfDocs2[0]):
                #print(listOfDocs1[0]+" ---> "+str(dGapsDecoder(listOfDocs1[1]))+" ::: "+listOfDocs2[0]+" ----> "+str(dGapsDecoder(listOfDocs2[1])))
               if findAdjecency(dGapsDecoder(listOfDocs1[1]), dGapsDecoder(listOfDocs2[1]), proximityWindow) == True:
                   #print(listOfDocs1[0] + " ---> " + str(dGapsDecoder(listOfDocs1[1])) + " ::: " + listOfDocs2[0] + " ----> " + str(dGapsDecoder(listOfDocs2[1])))
                   f.write(listOfDocs1[0]+"\n")

    f.close()


# This is the main method.
def main():
    # getTheFiles()
    # getCleanCorpus("unigram")
    # getCleanCorpus("bigram")
    # getCleanCorpus("trigram")
    #buildSortedTermFrequencyTable("unigram")
    #buildSortedTermFrequencyTable("bigram")
     buildSortedTermFrequencyTable("trigram")
    # task3("carbon", "emission", 5)
    # task3("carbon", "emission", 10)
    # task3("greenhouse", "emission", 6)
    # task3("greenhouse", "emission", 12)



if __name__ == '__main__':
    main();