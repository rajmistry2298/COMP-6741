# COMP6741
Intelligent system - Project 1

#Accompanying documents
RDF Schema: Knowledge_base.ttl

Dataset: /datasets/course_data.csv, /datasets/content_data.csv, /datasets/lecture_data.csv, /datasets/event_data.csv, 

KB Construction: kbuilder.py

Knowledge Base: Knowledge_base.nt

Queries: /queries/

Queries result: /queries output/

Report: COMP_6741 Project Report.pdf

#How to run
1) Place University folder in the Fuseki server /webapp folder. Fuseki server should be running on localhost:3030
2) Run the kbuilder.py python file
    python kbuilder.py
3) Load the Knowledge_base.nt file in Apache Fuseki
4) Copy the PREFIX section into fuseki and the required sparql queries
