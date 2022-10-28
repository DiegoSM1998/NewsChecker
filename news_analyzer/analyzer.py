import pandas
import nltk
import time
import random
import re
import routes
import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from translate import Translator

from operator import itemgetter

from nltk.corpus import wordnet as wn

# Class word_token

class word_token:
    def __init__(self, word, synset, lex_class, wordnet_word):
        self.word       = word
        self.synset     = synset
        
        if wordnet_word == 1:
            if lex_class == 'n' or lex_class == 's':
                self.lex_class = 'noun_token'
            elif lex_class == 'v':
                self.lex_class = 'verb_token'
            elif lex_class == 'a':
                self.lex_class = 'adjective_token'
            elif lex_class == 'r':
                self.lex_class = 'adverb_token'

        else:
            self.lex_class  = lex_class

# Functions to tinker with the dataset

def load_news_text(route_database):
    dataframe_full          = pandas.read_csv(route_database)
    data_news_full          = pandas.DataFrame(dataframe_full['text'])
    
    print(data_news_full)

    return data_news_full

# Functions to analyze descriptions (LEXICAL)

def converse_to_tokens(words_to_tokenize):
    # Meter tokens especificos para los pronombres
    # I         ---> i_token
    # You       ---> you_token
    # He        ---> he_token
    # She       ---> she_token
    # It        ---> it_token
    # We        ---> we_token
    # They      ---> they_token

    # Initialization
    token_list          = []
    similarity_list     = []
    smaller_similarity   = 0
    
    translator= Translator(to_lang="en", from_lang="es")    

    # Lists pronouns

    pronombres_det_demostrativos            = ['aquel', 'aquella', 'aquellos','aquellas','esa','esas',
                                                'ese', 'esos', 'esta', 'estas','este','estos']
    
    pronombres_det_posesivos                = ['mi', 'mis', 'tu', 'tus', 'su', 'sus', 'nuestra', 'nuestras', 'nuestro',
                                                'nuestros', 'vuestra', 'vuestras', 'vuestro', 'vuestros', 'suya',
                                                'suyas', 'suyo', 'suyos']

    determinantes_interrogativos            = ['cuánta', 'cuántas', 'cuánto', 'cuántos', 'qué']
    
    determinantes_indefinidos               = ['alguna', 'algunas', 'alguno', 'algún', 'algunos', 'bastante', 'bastantes', 'cada',
                                                'ninguna', 'ningunas', 'ninguno', 'ningún', 'ningunos', 'otra', 'otras', 'otro', 'otros',
                                                'sendas', 'sendos', 'tantas', 'tantos', 'tanto', 'todas', 'toda', 'todos', 'todo', 'unas',
                                                'una', 'unos', 'un', 'varias', 'varios']
    
    determinantes_articulos                 = ['el', 'la', 'los', 'las']

    pronombres_personales_tonicos           = ['yo', 'tu', 'él', 'ella', 'nosotros', 'nosotras', 'vosotros', 'vosotras', 'ellos', 'ellas']

    pronombres_personales_atonos            = ['me', 'te', 'se', 'nos' 'os']
    
    preposiciones                           = ['a', 'al', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'del', 'desde', 'en', 'entre', 'hacia', 'hasta', 'para', 
                                               'por', 'según', 'sin', 'sobre', 'tras', 'durante', 'mediante']
    
    number_expresion                        = re.compile(r"[\d]+[%+\-*]*")
    nombre_propio_expresion                 = re.compile(r"[A-Z][a-z]+")
    siglas_expresion                        = re.compile(r"[A-Z][A-Z]+")
    
    
    # Processing_words
    
    for word in words_to_tokenize:
        word_index              = words_to_tokenize.index(word)
        word = word.replace('“', '')
        similarity_list         = []
        smaller_similarity       = 0
        has_meaning             = False
        
        if word.lower() in pronombres_personales_tonicos:
            token_list.append(word_token(word, None, 'pronombre_personal_tonico_token', 0))
            continue

        elif  word.lower() in pronombres_det_posesivos:
            token_list.append(word_token(word, None, 'pronombres_det_posesivos_token', 0))
            continue

        elif word.lower() in determinantes_interrogativos:
            token_list.append(word_token(word, None, 'determinantes_interrogativos_token', 0))
            continue

        elif word.lower() in determinantes_indefinidos:
            token_list.append(word_token(word, None, 'determinantes_indefinidos_token', 0))
            continue

        elif word.lower() in determinantes_articulos:
            token_list.append(word_token(word, None, 'determinantes_articulos_token', 0))
            continue

        elif word.lower() in pronombres_personales_tonicos:
            token_list.append(word_token(word, None, 'pronombres_personales_tonicos_token', 0))
            continue

        elif word.lower() in pronombres_personales_atonos:
            token_list.append(word_token(word, None, 'pronombres_personales_atonos_token', 0))
            continue

        elif word.lower() in preposiciones:
            token_list.append(word_token(word, None, 'preposiciones_token', 0))
            continue        
        
        elif number_expresion.findall(word) != []:
            token_list.append(word_token(word, None, 'numeric_expresion_token', 0))
            continue

        else:
            if word_index != len(words_to_tokenize) - 1:
                synsets_list        = wn.synsets(word, lang='spa')
                next_synsets_list   = wn.synsets(words_to_tokenize[word_index + 1], lang='spa')
            else:
                synsets_list        = wn.synsets(word, lang='spa')
                next_synsets_list   = wn.synsets(words_to_tokenize[word_index - 1], lang='spa')

            if next_synsets_list != []:
                if synsets_list > next_synsets_list:
                    bigger_list     = synsets_list
                    smaller_list    = next_synsets_list
                else:
                    bigger_list     = next_synsets_list
                    smaller_list    = synsets_list
    
                for big_synset in  bigger_list:
                    similarities = map(big_synset.path_similarity, smaller_list)
                    similarity_list.append(list(similarities))
    
                for index in range(len(similarity_list)):
    
                    aux_list = [similarity_list[index].index(simil) for simil in similarity_list[index] if simil != None]
    
                    for index_simil in aux_list:
                        if similarity_list[index][index_simil] < smaller_similarity:
                            smaller_similarity = similarity_list[index][index_simil]
    
                # Sometimes all the meanings had the same shortest path to the next word
                # so, we take only the first of all the coincidence
                for simil in similarity_list:
                    if bigger_list == synsets_list and has_meaning == False:
                        if smaller_similarity in simil:
                            meaning_def = [similarity_list.index(simil)]
                            kind_of_word = meaning_def.name().split('.')
    
                            if word != 'okay':
                                token_list.append(word_token(word, meaning_def.definition(), kind_of_word[1], 1))
                            else:
                                token_list.append(word_token(word, meaning_def.definition(), kind_of_word[3], 1))
                            has_meaning = True
    
                    elif bigger_list == next_synsets_list and has_meaning == False:
                        if smaller_similarity in simil:
                            meaning_def = wn.synsets(word, lang='spa')[simil.index(smaller_similarity)]
                            kind_of_word = meaning_def.name().split('.')
    
                            if word != 'okay':
                                token_list.append(word_token(word, meaning_def.definition(), kind_of_word[1], 1))
                            else:
                                token_list.append(word_token(word, meaning_def.definition(), kind_of_word[3], 1))
                            has_meaning = True
                    
                if has_meaning == False and len(wn.synsets(word, lang='spa')) > 0:
                    meaning_def = wn.synsets(word, lang='spa')[0]
                    kind_of_word = meaning_def.name().split('.')
    
                    if word != 'okay':
                        token_list.append(word_token(word, meaning_def.definition(), kind_of_word[1], 1))
                    else:
                        token_list.append(word_token(word, meaning_def.definition(), kind_of_word[3], 1))
    
                    has_meaning = True
            else:
                try:
                    if word != "":                
                        if nombre_propio_expresion.findall(word) != [] or siglas_expresion.findall(word):    
                            
                            if wn.synsets(word, lang='spa') != []:
                                token_list.append(word_token(word, wn.synsets(word, lang='spa')[0], wn.synsets(word, lang='spa')[0].name().split('.')[1], 1))
                            
                            else:
                                token_list.append(word_token(word, None, 'nombres_propios_token', 0))
    
                        
                        else:
                            word_traduced = translator.translate(word).lower().split(' ')
                        
                            if len(word_traduced) > 1:
                                word_traduced = word_traduced[len(word_traduced) - 1]
                            else:
                                word_traduced = word_traduced[0]
                            
                            token_list.append(word_token(word, wn.synsets(word_traduced)[0], wn.synsets(word_traduced)[0].name().split('.')[1], 1))
                except:
                    continue
                    
    return token_list

def lexical_analysis(descriptions_complete):
    # Taking full descriptions and split by lines
    
    descriptions_list           = descriptions_complete.split('\n')
    descriptions_splitted       = []
    descriptions_corrected      = []

    words_to_process            = []

    tokenize_description        = []
    tokenized_descriptions_full = []

    for description in descriptions_list:
        description_aux = split_descriptions(description)

        # To avoid including empty descriptions lists in 
        # the main container to descriptions

        if len(description_aux) > 0:
            descriptions_splitted.append(description_aux)

    for description in descriptions_splitted:
        words_to_process = []
        for line in description:
            words_to_correct = line.split(' ')
            
            if len(words_to_correct) > 0:
                words_to_process.append(words_to_correct)

            words_to_process_def = []
            
            for phrase_list in words_to_process:
                new_phrase = []
                
                for word in phrase_list:
                    word = word.replace('!', '').replace('?', '').replace(',','').replace('.', '')

                    if ' ' in word:
                        for new_word in word.split(' '):
                            new_phrase.append(new_word)
                    else:
                        new_phrase.append(word)
                
                words_to_process_def.append(new_phrase)

        # We made this, to split the descriptions in list like:
        #           one description
        # [ [[phrase], [phrase], [phrase]] ]
        # |                                |
        # |_______________\/_______________| 
        #           all descriptions
    
        descriptions_corrected.append(words_to_process_def)
    
    for description in descriptions_corrected:
        tokenize_description = []

        for line in description:
           tokenize_description.append(converse_to_tokens(line))
    
        tokenized_descriptions_full.append(tokenize_description)

    return tokenized_descriptions_full

def split_descriptions(description):
    # Taking the splitted descriptions by lines and split by separators:
    #       - (), [], {} Lo consideramos como una linea a parte
    #       - ' ', ;, '\t'
    # Aplanar listas mas tarde

    splitted_by_lines           = description.split('. ')
    line_fragments_1            = []
    line_fragments_2            = []

    for splitted_fragment in splitted_by_lines:
        splitted_aux = splitted_fragment.split(' (')
        line_fragments_1.append(splitted_aux)

    line_fragments_1 = [y for x in line_fragments_1 for y in x]

    for splitted_fragment in line_fragments_1:
        splitted_aux = splitted_fragment.split(') ')
        line_fragments_2.append(splitted_aux)

    line_fragments_2 = [y for x in line_fragments_2 for y in x]
    line_fragments_1 = []

    for splitted_fragment in line_fragments_2:
        splitted_aux = splitted_fragment.split('; ')
        line_fragments_1.append(splitted_aux)

    # Remove duplicates in list, with set conversion
    line_fragments_1    = [y for x in line_fragments_1 for y in x]
    line_fragments_1    = set(line_fragments_1)
    line_fragments_1    = list(line_fragments_1)

    # Remove void strings list from description
    if '' in line_fragments_1:
        line_fragments_1.remove('')

    if ' ' in line_fragments_1:
        line_fragments_1.remove(' ')

    return line_fragments_1

def write_lexical_analysis_result(descriptions):
    
    file_output = open(routes.lexical_sequence, 'w')

    for descriptions_tokens_sequence in descriptions:    
        for description in descriptions_tokens_sequence:
            for phrases in description:
                phrase_to_write = ""
                
                for word in phrases:
                    phrase_to_write += "{} ".format(word.lex_class)
    
                phrase_to_write += "\n"
                file_output.write(phrase_to_write)

    print("[*] Tokens dataset write!")

# Functions to analyze descriptions (SINTACTIC) WIP
def compose_dataset_to_sintactic_analysis():
    # Naive Bayes
    # previous_token actual_token next_token
    # if actual token is first_token_in_phrase
    #   then previous_token = void_token
    # elif actual token is last_token_in_phrase:
    #   then next_token = void_token
    # else:
    #   fill_dataset(previous_token, actual_token, last_token)
    
    file_sequence       = open(routes.lexical_sequence, 'r')
    line                = file_sequence.readline()
    list_to_dataframe    = []

    previous_token  = ''
    next_token      = ''
    actual_token    = ''
    first_word      = 0
    last_word       = 0
    
    while line:
        line_list_aux   = line.split(' ')
        long_list       = len(line_list_aux) - 1
        
        for token in line_list_aux:
            token_index     = line_list_aux.index(token)

            if token_index == 0:
                previous_token  = 'void_token'
                actual_token    = token
                first_word      = 1
            
                if token_index == long_list:
                    next_token      = 'void_token'
                    last_word       = 1
                else:
                    next_token      = line_list_aux[token_index + 1]

            
            if token_index == long_list:
                next_token      = 'void_token'
                actual_token    = token
                last_word       = 1

                if token_index == 0:
                    previous_token  = 'void_token'
                    first_word       = 1

                else:
                    previous_token  = line_list_aux[token_index - 1]

            
            if token_index != 0 and token_index != long_list:
                previous_token  = line_list_aux[token_index - 1]
                actual_token    = token
                next_token      = line_list_aux[token_index + 1]
                
            list_to_dataframe.append([previous_token, actual_token, next_token, first_word, last_word])
            
            previous_token  = ''
            next_token      = ''
            actual_token    = ''
            first_word      = 0
            last_word       = 0
            
        line = file_sequence.readline()
    
    col_names = ['previous_token', 'actual_token', 'next_token',
                 'first_word', 'last_word']
    
    return pd.DataFrame(np.array(list_to_dataframe), columns=col_names)

# Functions to analyze descriptions (SEMANTIC)

def analyze_exec():

    print("[*] Beggining preprocess and analysis...")
    news_text = load_news_text(routes.database_example)

    return lexical_analysis(news_text)

def mix_tokens_with_database(route_database, route_tokens_sequence):
    dataframe_database          = load_news_text(route_database)
    
    descriptions_list           = list(dataframe_database['text'])
    lexical_sequences           = []
    
    for description in descriptions_list:
         
        lexical_sequences.append(lexical_analysis(description))        

    return lexical_sequences

def exec_routine(list_execution):
    execution_orders = []

    if len(list_execution) > 3:
        print("[*] FAIL. Wrong number of arguments")
        print("\t[*] Usage: -p (traduce) (label) (analyze)")

    else:
        for command in list_execution:
            if command != 'traduce' and command != 'analyze' and command != 'label' and command != 'test':
                print("[*] FAIL. Wrong arguments")
                print("\t[*] Usage: -p (traduce) (label) (analyze) (test)")
    
    if 'analyze' in list_execution:
        sequence_tokens_descriptions = analyze_exec()
        write_lexical_analysis_result(sequence_tokens_descriptions)

    if 'test' in list_execution:
        mix_tokens_with_database(routes.database_example, routes.lexical_sequence)


                
