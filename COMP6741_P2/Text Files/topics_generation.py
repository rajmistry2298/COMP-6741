import os
import json
import csv
import urllib.parse
import pandas
import requests

def generate_topics(courseID, lectureID, filePath):
    path = r"C:\Users\rajmi\Documents\GitHub\COMP6741\datasets\\"
    topics_file_exist = os.path.isfile(path+'lab_topics.csv')
    with open(path+'lab_topics.csv', 'a+', newline='') as topics_csv:
        topics_csv.seek(0)
        topics_csv_columns = ['Course ID', 'Lecture ID', 'Topic Name', 'Topic Link']
        writer = csv.DictWriter(topics_csv, fieldnames=topics_csv_columns)
        if not topics_file_exist:
            writer.writeheader()
        
        file = open(filePath, 'r', encoding="UTF-8")
        count = 1
        while True:
            # Get next line from file
            line = file.readline()
            # if line is empty
            # end of file is reached
            if not line:
                break
            print("Line{}: {}".format(count, line.strip()))
            count = count + 1
            data = line.strip()
            try:
                base_url = 'http://localhost:2222/rest/annotate?text={text}&confidence={confidence}&support={support}'
                confidence = '0.9'
                support = '0'
                request = base_url.format(text=urllib.parse.quote_plus(data), confidence=confidence, support=support)
                headers = {'Accept': 'application/json'}
                request = requests.get(url=request, headers=headers)
                response = json.loads(request.content)
                print("---------------------------------------Response Content is Here---------------------------------------")
                print(response)
                print("------------------------------------------------------------------------------------------------------")
                if 'Resources' in response:
                    resources = response['Resources']
                    print("---------------------------------Resources are here------------------------------------------------")
                    print(resources)
                    print("---------------------------------------------------------------------------------------------------")
                    topics_list = list()
                    for resource in resources:
                        surface_form = resource['@surfaceForm']
                        print("----------------------------surfaceForm here----------------------------------------------------")
                        print(surface_form)
                        print("------------------------------------------------------------------------------------------------")
                        uri = resource['@URI']
                        topic = dict()
                        topic['Course ID'] = courseID
                        topic['Lecture ID'] = lectureID
                        topic['Topic Name'] = surface_form
                        topic['Topic Link'] = uri
                        topics_list.append(topic)
                    for topic in topics_list:
                        print("------------------------------Topic---------------------------")
                        print(topic)
                        writer.writerow(topic)
                        print("--------------------------------------------------------------")
            except json.JSONDecodeError:
                print("Error") 
        file.close()

if __name__ == "__main__":
    IS_Text_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6741"
    AI_Text_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6721"
    IS_Worksheet_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6741\worksheet"
    AI_Worksheet_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6721\worksheet"
    IS_Lab_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6741\lab"
    AI_Lab_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6721\lab"
    
    
    lectureCount = 1
    for txtfile in os.listdir(IS_Text_directory):
       print(str(txtfile))
       generate_topics('40355', lectureCount, IS_Text_directory+'\\'+txtfile)
       lectureCount = lectureCount+1
   
    lectureCount = 1
    for txtfile in os.listdir(AI_Text_directory):
        print(str(txtfile))
        generate_topics('40353', lectureCount, AI_Text_directory+'\\'+txtfile)
        lectureCount = lectureCount+1
   
    lectureCount = 2
    for txtfile in os.listdir(IS_Worksheet_directory):
        print(str(txtfile))
        generate_topics('40355', lectureCount, IS_Worksheet_directory+'\\'+txtfile)
        lectureCount = lectureCount+1
  
    lectureCount = 2
    for txtfile in os.listdir(AI_Worksheet_directory):
        print(str(txtfile))
        generate_topics('40353', lectureCount, AI_Worksheet_directory+'\\'+txtfile)
        lectureCount = lectureCount+1