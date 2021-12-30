import tika
from tika import parser
import os
tika.initVM()

IS_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\University\COMP6741\Worksheets"
AI_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\University\COMP6721\Worksheets"
IS_Save_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6741\worksheet"
AI_Save_directory = r"C:\Users\rajmi\Documents\GitHub\COMP6741\Text Files\COMP6721\worksheet"

i=1
print("---------------------------Intelligent System-------------------------------")
for file in os.listdir(IS_directory):
    print("--------------------"+file+"--------------------------------------------")
    parsedfile = parser.from_file(IS_directory + "\\" + file)
    f = open(IS_Save_directory+'\\worksheet'+str(i)+'.txt','w', encoding='UTF-8')
    file_string_with_blank_lines = parsedfile["content"].strip()
    lines = file_string_with_blank_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    file_string_without_empty_lines = ""
    lines_seen = set()
    for line in non_empty_lines:
        if line not in lines_seen: # not a duplicate
            file_string_without_empty_lines += line.strip() + "\n"
            lines_seen.add(line)
    f.write(file_string_without_empty_lines)
    f.close()
    print("Done Wrting worksheet-"+str(i))
    i=i+1

j=1
print("---------------------------Artificial Intelligence-------------------------------")
for file in os.listdir(AI_directory):
    print("--------------------"+file+"--------------------------------------------")
    parsedfile = parser.from_file(AI_directory + "\\" + file)
    f = open(AI_Save_directory+'\\worksheet'+str(j)+'.txt','w', encoding='UTF-8')
    file_string_with_blank_lines = parsedfile["content"].strip()
    lines = file_string_with_blank_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    file_string_without_empty_lines = ""
    lines_seen = set()
    for line in non_empty_lines:
        if line not in lines_seen: # not a duplicate
            file_string_without_empty_lines += line.strip() + "\n"
            lines_seen.add(line)
    f.write(file_string_without_empty_lines)
    f.close()
    print("Done Wrting Worksheet-"+str(j))
    j=j+1