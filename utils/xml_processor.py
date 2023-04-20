# This code is heavily based on this notebook: https://github.com/mahesh-keswani/med-quad-mlm-bert/blob/main/ProcessData.ipynb

import json
import os
import xmltodict
import re
import time

import git
import pandas as pd
from jsonpath import jsonpath


BASE_PATH = "../clean_data"
RAW_DATA_PATH = "../raw_data"
MEDQUAD_REPO_URL = 'git@github.com:abachaa/MedQuAD.git'
data = {"Questions": [], "Answers": [], "Focus": []}


def processXmlFile(completePath):
    with open(completePath) as f:
        xmlstring = f.read()
        try:
            dataDict = xmltodict.parse(xmlstring, xml_attribs=False)
            listOfQA = json.loads(json.dumps(jsonpath(dataDict, "$.." + "QAPair")[0]))
            focus = json.loads(json.dumps(jsonpath(dataDict, "$.." + "Focus")[0]))
        except Exception as e:
            # i.e either QAPair is empty OR Focus
            return

        # if there is only single QA, then it will be dict instead of list
        if isinstance(listOfQA, dict):
            listOfQA = [listOfQA]

        for qaPair in listOfQA:
            try:
                # remove the extra spaces from answer with single space
                x = re.sub(" +", " ", qaPair["Answer"])
                x = re.sub("Key Points", "", x)
                x = x.replace("\n", "").replace("-", "")
                data["Answers"].append(x)
                data["Questions"].append(qaPair["Question"])
                data["Focus"].append(focus)
            except:
                return

def download_med_qa_dataset():
    if os.path.exists(RAW_DATA_PATH):
        git.Repo.clone_from(
            MEDQUAD_REPO_URL,
            RAW_DATA_PATH,
            branch="master")
    else:
        os.mkdir(RAW_DATA_PATH)
        download_med_qa_dataset()

foldersWithEmptyAnswers = [
    ".git",
    "10_MPlus_ADAM_QA",
    "11_MPlusDrugs_QA",
    "12_MPlusHerbsSupplements_QA",
    "readme.txt",  # As it does not contain any QAs
    "QA-TestSet-LiveQA-Med-Qrels-2479-Answers.zip",  # will use it later,
    "ProcessedData.csv",
]

download_med_qa_dataset()

for folder in os.listdir(RAW_DATA_PATH):
    if folder in foldersWithEmptyAnswers:
        continue
    else:
        print("Processing folder:", folder)
        start = time.time()

        for xmlFileName in os.listdir(os.path.join(RAW_DATA_PATH, folder)):
            completePath = os.path.join(RAW_DATA_PATH, folder, xmlFileName)
            processXmlFile(completePath)

        print("Took", time.time() - start)


df = pd.DataFrame(data)
df.head()
df.to_csv(BASE_PATH + "/ProcessedData.csv", index=False)
