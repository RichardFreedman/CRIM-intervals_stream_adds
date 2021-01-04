import streamlit as st
from pathlib import Path
import requests
import pandas as pd
from pandas.io.json import json_normalize
import base64
from crim_intervals import *
import ast
from itertools import tee, combinations
from typing import List
# import matplotlib





#sets up function to call Markdown File for "about"
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

# download function for output csv's

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

# functions for pairs of ratios

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def get_ratios(input_list):
    ratio_pairs = []
    for a, b in pairwise(input_list):
        ratio_pairs.append(b / a)
    return ratio_pairs

# Here we group the rows in the DF by the Pattern Generating Match
# Each has its own string of durations, and duration ratios
# and then we compare the ratios to get the differences
# the "list(combinations)" method takes care of building the pairs, using data from our dataframe 'results'

def compare_ratios(ratios_1, ratios_2):
    
    ## division of lists 
    # using zip() + list comprehension 
    diffs = [i - j for i, j in zip(ratios_1, ratios_2)] 
    abs_diffs = [abs(ele) for ele in diffs] 
    sum_diffs = sum(abs_diffs)

    return sum_diffs

#results["Pattern_Generating_Match"] = results["Pattern_Generating_Match"].apply(tuple) 

def get_ratio_distances(results, pattern_col, output_cols):
    
    matches = []

    for name, group in results.groupby(pattern_col):

        ratio_pairs = list(combinations(group.index.values, 2))

        for a, b in ratio_pairs:
            
            a_match = results.loc[a]
            b_match = results.loc[b]
            
            sum_diffs = compare_ratios(a_match.duration_ratios, b_match.duration_ratios)
            
            match_dict = {
                "pattern": name,
                "sum_diffs": sum_diffs
            }
            
            for col in output_cols:
                match_dict.update({
                    f"match_1_{col}": a_match[col],
                    f"match_2_{col}": b_match[col]
                })
                
            matches.append(match_dict)
            
    return pd.DataFrame(matches)


# classifier output to pandas


def classified_matches_to_pandas(matches):
    
    soggetti_matches = []
    
    for i, cm in enumerate(matches):
        
        for j, soggetti in enumerate(cm.matches):
            
            soggetti_matches.append({
                "piece": soggetti.first_note.metadata.title,
                "type": cm.type,
                "part": soggetti.first_note.part.strip("[] "),
                "start_measure": soggetti.first_note.note.measureNumber,
                "soggetto_number": j + 1,
                "pattern": cm.pattern,
                "match_number": i + 1
            })
    return pd.DataFrame(soggetti_matches)
# work lists

WorkList_mei = ['CA_Brumel_01.mei_msg.mei',
 'CA_Brumel_02.mei_msg.mei',
 'CA_Brumel_03.mei_msg.mei',
 'CA_Brumel_04.mei_msg.mei',
 'CA_Brumel_05.mei_msg.mei',
 'CA_Guerrero_Missa_Congratulamini_1.mei_msg.mei',
 'CA_Guerrero_Missa_Congratulamini_2.mei_msg.mei',
 'CA_Guerrero_Missa_Congratulamini_3.mei_msg.mei',
 'CA_Guerrero_Missa_Congratulamini_4.mei_msg.mei',
 'CA_Guerrero_Missa_Congratulamini_5.mei_msg.mei',
 'CA_Guerrero_Missa_Congratulamini_6.mei_msg.mei',
 'CA_Guerrero_Missa_sancta_et_immaculata_1.mei_msg.mei',
 'CA_Guerrero_Missa_sancta_et_immaculata_2.mei_msg.mei',
 'CA_Guerrero_Missa_sancta_et_immaculata_3.mei_msg.mei',
 'CA_Guerrero_Missa_sancta_et_immaculata_4.mei_msg.mei',
 'CA_Guerrero_Missa_sancta_et_immaculata_5.mei_msg.mei',
 'CA_Guerrero_Missa_sancta_et_immaculata_6.mei_msg.mei',
 'CA_Lasso_Missa_Doulce_1.mei_msg.mei',
 'CA_Lasso_Missa_Doulce_2.mei_msg.mei',
 'CA_Lasso_Missa_Doulce_3.mei_msg.mei',
 'CA_Lasso_Missa_Doulce_5.mei_msg.mei',
 'CA_Sandrin_Doulce_msg.mei',
 'CA_Recordare.mei_msg.mei'
]


# general headers for main window

#WorkList = ['CRIM_Model_0001.mei']
st.header("CRIM Project:  CRIM Intervals")

st.subheader("Python Scripts for Analysis of Similar Soggetti in Citations: The Renaissance Imitation Mass")
st.write("Visit the [CRIM Project](https://crimproject.org) and its [Members Pages] (https://sites.google.com/haverford.edu/crim-project/home)")
st.write("Also see the [Relationship Metadata Viewer] (https://crim-relationship-data-viewer.herokuapp.com/) and [Observation Metadata Viewer] (https://crim-observation-data-viewer.herokuapp.com/)")



st.sidebar.subheader("Step 1: Choose Piece(s) from CRIM pending additions")
st.sidebar.write("Select Works with Menu, or Type ID, such as 'Model_0008'")
selected_works = st.sidebar.multiselect('', WorkList_mei)
print_list = pd.DataFrame(selected_works)
st.write("Your Selections:")
st.write(print_list)
#st.write(selected_works)



#st.write(selected_works)
# correct URL for MEI 4.0
WorkList_mei = [el.replace("CA_", "https://raw.githubusercontent.com/RichardFreedman/CRIM_additional_works/main/") for el in selected_works]

@st.cache(allow_output_mutation=True)
def load_corpusbase(WorkList_mei:List):
    corpus = CorpusBase(WorkList_mei)
    return corpus

# Now pass the list of MEI files to Crim intervals
#@st.cache(allow_output_mutation=True)
#if st.sidebar.button('Load Selections'):
corpus = load_corpusbase(WorkList_mei)

# Correct the MEI metadata

import xml.etree.ElementTree as ET
import requests

MEINSURI = 'http://www.music-encoding.org/ns/mei'
MEINS = '{%s}' % MEINSURI

for i, path in enumerate(WorkList_mei):
    
    try:
        if path[0] == '/':
            mei_doc = ET.parse(path)
        else:
            mei_doc = ET.fromstring(requests.get(path).text)

      # Find the title from the MEI file and update the Music21 Score metadata
        title = mei_doc.find('mei:meiHead//mei:titleStmt/mei:title', namespaces={"mei": MEINSURI}).text
        print(path, title)
        corpus.scores[i].metadata.title = title
    except:
        continue

# Header

# Select Actual or Incremental Durations
st.sidebar.subheader("Step 2:  Select Rhythmic Preference")
duration_choice = st.sidebar.radio('Select Actual or Incremental Durations', ["Actual","Incremental@1","Incremental@2", "Incremental@4"])

if duration_choice == 'Actual':
    vectors = IntervalBase(corpus.note_list)
elif duration_choice == 'Incremental@1':
    vectors = IntervalBase(corpus.note_list_incremental_offset(1))
elif duration_choice == 'Incremental@2':
    vectors = IntervalBase(corpus.note_list_incremental_offset(2))
elif duration_choice == 'Incremental@4':
    vectors = IntervalBase(corpus.note_list_incremental_offset(4))
else:
    st.write("Please select duration preference")
# Select Generic or Semitone
st.sidebar.subheader("Step 3:  Select Interval Preference")
scale_choice = st.sidebar.radio('Select Diatonic or Chromatic', ["Diatonic","Chromatic"])

if scale_choice == 'Diatonic':
    scale = vectors.generic_intervals
elif scale_choice == 'Chromatic':
    scale = vectors.semitone_intervals
else:
    st.write("Please select duration preference")

# Select Vector Length and Minimum Number of Matches
st.sidebar.subheader("Step 4:  Select Vectors, Matches, and Thresholds")

vector_length = st.sidebar.number_input("Enter a Number for the Length of Vector, or use default", min_value=1, max_value=20, value=5)

minimum_match = st.sidebar.number_input("Enter a Minimum Number of Matches, or use default", min_value=1, max_value=20, value=3)

close_distance = st.sidebar.number_input("If Close Search, then Enter Threshold, or use default", min_value=1, max_value=20, value=2)

max_sum_diffs = st.sidebar.number_input("Enter Maximum Durational Differences (Whole Number or Fractional Value), or use default", min_value=None, max_value=None, value=2)

patterns = into_patterns([scale], vector_length)

# Select Exact or Close

st.sidebar.subheader("Step 5: Search for Similar Melodies")
st.sidebar.write("Adjust Time and Melodic Scales, Vectors, Minimum Matches, and Melodic Flex in Steps 2, 3, 4 at left, or use defaults") 
#exact_close_choice = st.sidebar.radio('Select Exact or Close Match (if Close, then Select Treshold Above)', ["No Selection", "Exact", "Close"])


if st.sidebar.button('Run Exact Search'):
    patterns = into_patterns([scale], vector_length)
    find_matches = find_exact_matches(patterns, minimum_match)
    output = export_pandas(find_matches)
    #pd.DataFrame(output).head()
    results = pd.DataFrame(output)
    st.write('Output of Exact Melodic Pattern Search')
    st.write(results)
    st.subheader("Optional:  Download CSV of Exact Melodies from Step 5")
    s1 = st.text_input('Provide filename for melodic pattern match download (must include ".csv")')
    tmp_download_link = download_link(results, s1, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)
if st.sidebar.button('Run Close Search'):
    patterns = into_patterns([scale], vector_length)
    find_matches = find_close_matches(patterns, minimum_match, close_distance)
    output = export_pandas(find_matches)
    #pd.DataFrame(output).head()
    results = pd.DataFrame(output)
    st.write('Output of Close Melodic Pattern Search')
    st.write(results)
    st.subheader("Optional:  Download CSV of Close Melodies from Step 5")
    s2 = st.text_input('Provide filename for melodic pattern match download (must include ".csv")')
    tmp_download_link = download_link(results, s2, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


#minimum_match = st.slider('Minimum Number of Matches for Each Vector', min_value=2, max_value=20)
# st.subheader("Step 6: Run Melodic Similarity Search")
# if st.button('Run Melodic Search'):
#     #patterns = into_patterns([scale], vector_length)
#     #exact_matches = find_exact_matches(patterns, minimum_match)
#     #find_matches
#     output = export_pandas(find_matches)
#     #pd.DataFrame(output).head()
#     results = pd.DataFrame(output)
#     st.write('Output of Melodic Pattern Search')
#     st.write(results)

    # Option to download CSV of the first-stage results
    # st.subheader("Optional:  Download CSV from Step 6")
    # s1 = st.text_input('Provide filename for melodic pattern match download (must include ".csv")')
    # tmp_download_link = download_link(results, s1, 'Click here to download your data!')
    # st.markdown(tmp_download_link, unsafe_allow_html=True)

    # Stage 2 Rhythmic Simliarities Search
    
st.sidebar.subheader("Step 6: Search with Duration Filter")

if st.sidebar.button('Run Exact Search with Duration Filter'):
    patterns = into_patterns([scale], vector_length)
    find_matches = find_exact_matches(patterns, minimum_match)

    output = export_pandas(find_matches)
    results = pd.DataFrame(output)
    st.write('Output of Exact Melodic Pattern Search')
    
    # clean-up results of melodic match:  chance patterns to tuples 
    results["pattern_generating_match"] = results["pattern_generating_match"].apply(tuple)

    # clean-up column titles

    # results.rename(columns=
    #                {'Pattern Generating Match': 'Pattern_Generating_Match', 
    #                 'Pattern matched':'Pattern_Matched',
    #                 'Piece Title': 'Piece_Title',
    #                 'First Note Measure Number': 'Start_Measure',
    #                 'Last Note Measure Number': 'Stop_Measure',
    #                 'Note Durations': 'Note_Durations'
    #                },
    #                 inplace=True)

    # evaluation Note_Durations as literals--only needed if we're importing CSV

    #results['note_durations'] = results['note_durations'].apply(ast.literal_eval)
    
    durations = results['note_durations']
    
    # calculates 'duration ratios' for each soggetto, then adds this to the DF

    results["duration_ratios"] = results.note_durations.apply(get_ratios)
    
    st.write(results)

    # now we calculate the _distances_ between pairs of ratios

    ratio_distances = get_ratio_distances(results, "pattern_generating_match", ["piece_title", "part", "start_measure", "end_measure"])

    ratios_filtered = ratio_distances[ratio_distances.sum_diffs <= max_sum_diffs]
    st.write("Results Filtered Distances of Durational Ratios")
    st.write(ratios_filtered)

    st.subheader("Optional:  Download CSV of Exact Melodies and Durations from Step 6")
    s3 = st.text_input('Provide filename for durational match download (must include ".csv")')
    tmp_download_link = download_link(ratios_filtered, s3, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

if st.sidebar.button('Run Close Search with Duration Filter'):
    patterns = into_patterns([scale], vector_length)
    find_matches = find_close_matches(patterns, minimum_match, close_distance)

    output = export_pandas(find_matches)
    results = pd.DataFrame(output)
    st.write('Output of Close Melodic Pattern Search')
    
    # clean-up results of melodic match:  chance patterns to tuples 
    results["pattern_generating_match"] = results["pattern_generating_match"].apply(tuple)

    # clean-up column titles

    # results.rename(columns=
    #                {'Pattern Generating Match': 'Pattern_Generating_Match', 
    #                 'Pattern matched':'Pattern_Matched',
    #                 'Piece Title': 'Piece_Title',
    #                 'First Note Measure Number': 'Start_Measure',
    #                 'Last Note Measure Number': 'Stop_Measure',
    #                 'Note Durations': 'Note_Durations'
    #                },
    #                 inplace=True)

    # evaluation Note_Durations as literals--only needed if we're importing CSV

    #results['note_durations'] = results['note_durations'].apply(ast.literal_eval)
    
    durations = results['note_durations']
    
    # calculates 'duration ratios' for each soggetto, then adds this to the DF

    results["duration_ratios"] = results.note_durations.apply(get_ratios)
    st.write("Results of Close Search with Duration Ratios Added")
    st.write(results)

    # now we calculate the _distances_ between pairs of ratios

    ratio_distances = get_ratio_distances(results, "pattern_generating_match", ["piece_title", "part", "start_measure", "end_measure"])

    ratios_filtered = ratio_distances[ratio_distances.sum_diffs <= max_sum_diffs]
    sort_by_measure = ratios_filtered.sort_values(["match_1_start_measure"])
    st.write("Results Filtered Distances of Durational Ratios")
    st.write(sort_by_measure)

    st.subheader("Optional:  Download CSV of Close Melodies and Durations from Step 6")
    s4 = st.text_input('Provide filename for durational match download (must include ".csv")')
    tmp_download_link = download_link(sort_by_measure, s4, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


# Classify Presentation Types

st.sidebar.subheader("Step : Classify Presentation Types")
st.sidebar.write('One Piece at a Time is Best!')

st.sidebar.write()
st.sidebar.write("Set Threshold of Durational Differences for Presentation Types.  NB:  This is different from the durational difference threshold set above")
st.sidebar.write()
max_sum_diffs_classify = st.sidebar.number_input("Enter Maximum Durational Differences Among Soggetti to be Classified (whole number only)", min_value=None, max_value=None, value=1)


if st.sidebar.button('Run Classifier with Exact Search'):
    find_matches = find_exact_matches(patterns, minimum_match)
    classified_matches = classify_matches(find_matches, max_sum_diffs_classify)
    classfied_output = classified_matches_to_pandas(classified_matches) 
    classified_results = pd.DataFrame(classfied_output)
    st.write()
    st.write("Presentation Types, Soggetti, and Voices")
    st.write(classified_results)
    st.subheader("Optional:  Download CSV of Classified Results")
    s4 = st.text_input('Provide filename for classified patterns (must include ".csv")')
    tmp_download_link = download_link(classified_results, s4, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)
    
if st.sidebar.button('Run Classifier with Close Search'):
    find_matches = find_close_matches(patterns, minimum_match, close_distance)
    classified_matches = classify_matches(find_matches, max_sum_diffs_classify)
    classfied_output = classified_matches_to_pandas(classified_matches) 
    classified_results = pd.DataFrame(classfied_output)
    st.write()
    st.write("Presentation Types, Soggetti, and Voices")
    st.write(classified_results)
    st.subheader("Optional:  Download CSV of Classified Results")
    s4 = st.text_input('Provide filename for classified patterns (must include ".csv")')
    tmp_download_link = download_link(classified_results, s4, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)




        
    
    


