# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json
import urllib

# Define queries to be used
#------------------------------------------------------------------------
PREFIXES = '''
            PREFIX unidata: <http://uni.io/data#> 
            PREFIX dcterms: <http://purl.org/dc/terms/> 
            PREFIX dcmitype: <http://purl.org/dc/dcmitype/> 
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX uni: <http://uni.io/schema#> 
            PREFIX dbo: <http://dbpedia.org/ontology/> 
            PREFIX dbr: <http://dbpedia.org/resource/> 
            PREFIX un: <http://www.w3.org/2007/ont/unit#> 
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            '''
# Params: subject, number
QUERY1 = PREFIXES+'''
            SELECT ?title ?description 
            WHERE { ?course dcmitype:subject "%s".
                    ?course dcmitype:identifier "%s".
                    ?course dcterms:title ?title .
                    ?course dcterms:description ?description .
                }
        '''
# Params: subject, number
QUERY2 = PREFIXES+'''SELECT ?lecture ?topic
            WHERE {
                ?course1 dcmitype:subject "%s".
                ?course1 dcmitype:identifier "%s".
                ?course1 dcterms:title ?course .
                ?lecture1 dcterms:isPartOf ?course1 .
                ?lecture1 dcmitype:identifier ?lecture .
                ?lecture1 uni:topic ?topic
            } ORDER BY ?lecture
            '''
# Params: subject, number, topic
QUERY3 = PREFIXES+'''SELECT ?lecture
            WHERE {
                ?course dcmitype:subject "%s".
                ?course dcmitype:identifier "%s".
                ?clecture dcterms:isPartOf ?course .
                ?clecture uni:topic <%s>.
                ?clecture dcmitype:identifier ?lecture
            }
            '''
# Params: None
QUERY4 = PREFIXES+'''SELECT (count(?courseId) as ?CourseCount)
            WHERE{
                ?courseId rdf:type uni:Course
            }
        '''

# Params: subject, number
QUERY5 = PREFIXES+'''SELECT ?number ?source
                    WHERE {
                        ?course dcmitype:subject "%s" .
                        ?course dcmitype:identifier "%s" .
                        ?lecture uni:hasContent ?content .
                        ?lecture dcterms:isPartOf ?course .
                        ?lecture dcmitype:identifier ?number .
                        ?content dcterms:type "READING" .
                        ?content dcterms:source ?source . 
                    } order by ?number
                '''

# Params: subject, number
QUERY6 = PREFIXES+'''SELECT ?lecture ?content_type ?source
                    WHERE {
                        ?course dcmitype:subject "%s" .
                        ?course dcmitype:identifier "%s" .
                        ?clecture uni:hasContent ?content .
                        ?clecture dcterms:isPartOf ?course .
                        ?clecture dcmitype:identifier ?lecture .
                        ?content dcterms:type ?content_type .
                        ?content dcterms:source ?source . 
                    } order by ?lecture
                '''

# Params: None
QUERY7 = PREFIXES+'''ASK
                        {
                            ?course1 dcmitype:subject "COMP" .
                            ?course1 dcmitype:identifier "6741" .
                            ?course1 uni:topic ?topic1 .
                            ?lecture1 dcterms:isPartOf ?course1 .
                            ?lecture1  uni:topic ?topic3 .
                            ?course2 dcmitype:subject "COMP" .
                            ?course2 dcmitype:identifier "6721" .
                            ?course2 uni:topic ?topic2 .
                            ?lecture2 dcterms:isPartOf ?course2 .
                            ?lecture1  uni:topic ?topic4 .
                            FILTER(?topic1 = ?topic2 || ?topic3 = ?topic4 ) .
                        }
                '''

# Params: None
QUERY8 = PREFIXES+'''SELECT (concat(?subject, " ", ?number) AS ?courseName)
                        WHERE {
                            ?course dcmitype:subject ?subject .
                            ?course dcmitype:identifier ?number .
                            ?lecture dcterms:isPartOf ?course .
                            ?lecture uni:topic dbr:Machine_learning .
                        }   ?courseId rdf:type uni:Course
                                    }
                '''

# Params: subject, number, type
QUERY9 = PREFIXES+'''ASK{
                        ?course dcmitype:subject "%s" .
                        ?course dcmitype:identifier "%s" .
                        ?lecture dcterms:isPartOf ?course .
                        ?event dcterms:isPartOf ?lecture .
                        ?event dcterms:type "%s".
                    }
                '''

QUERY10 = PREFIXES+'''SELECT ?topic
                WHERE {
                ?course dcmitype:subject "%s".
                ?course dcmitype:identifier "%s".
                ?lecture dcterms:isPartOf ?course .
                ?event dcterms:isPartOf ?lecture .
                ?event dcterms:type "%s".
                ?event dcmitype:identifier "%s".
                ?event uni:topic ?topic .
                }
            '''

QUERY11 = PREFIXES+'''SELECT ?courseName (count (?courseName) as ?count)
                    WHERE {

                    ?course rdf:type uni:Course.
                    ?lecture dcterms:isPartOf ?course .
                    ?event dcterms:isPartOf ?lecture .
                    ?event dcterms:type "LAB".
                    {?lecture uni:topic <%s>}  UNION {?event uni:topic <%s>}.
                    ?course dcterms:title ?courseName.                      

                    }  GROUP BY ?courseName ORDER BY DESC(?count)
            '''

QUERY13 = PREFIXES+'''SELECT (concat(?subject, " ", ?number) AS ?coursetitle) ?topic (count(?topic) as ?topicCount)
            WHERE {
                ?course dcmitype:subject ?subject .
                ?course dcmitype:identifier ?number .
                ?lecture dcterms:isPartOf ?course .
                ?lecture uni:topic <%s> .
                ?lecture uni:topic ?topic
            } GROUP BY ?subject ?number ?topic
            ORDER BY ?topicCount
            '''

QUERY12 = PREFIXES + '''SELECT  ?outline
                WHERE {
                    ?course rdf:type uni:Course .
                    ?course dcmitype:subject "%s" .
                    ?course dcmitype:identifier "%s" .
                    ?course uni:hasContent ?content .
                    ?content dcterms:type "OUTLINE" .
                    ?content dcterms:source ?outline .
                }
            '''

QUERY14 = PREFIXES + '''SELECT (concat(?subject, " ", ?number) AS ?courseName) ?title
            WHERE {
                ?course dcmitype:subject "%s" .
                ?course dcmitype:subject ?subject .
                ?course dcmitype:identifier ?number .
                ?course dcterms:title ?title .
            } ORDER BY ?number 
            '''
#------------------------------------------------------------------------

# Convert course string to subject and number
def course2dict(course):
    subject = course[0:4].upper()
    number = course[4:].strip()
    return {"subject": subject, "number":number}

def event2dict(event):
    e=""
    n=""
    a = event.split('#')
    e = a[0].upper()
    if len(a)>1:
        n = a[1]
    return{"event":e, "event_number":n}

# Convert topic to a dbpedia URI
def topic2URI(topic):
    topic_uri=''
    spotligh_url = 'http://api.dbpedia-spotlight.org/en/annotate?text={text}'
    header = {'accept': "application/json"}
    encode_topic = urllib.parse.quote(topic)
    print(spotligh_url.format(text=encode_topic))
    response = requests.get(spotligh_url.format(text=encode_topic), headers=header)

    response_dict = json.loads(response.text)
    print("Spotlight return:")
    print(response_dict)

    if 'Resources' in response_dict:
        topic_uri = response_dict['Resources'][0]['@URI']

    return topic_uri

def request2dict(query):
    fuseki_url = 'http://localhost:3030/uni/sparql'
    print('Fuseki Query: ' + query)
    httpresponse = requests.post(fuseki_url, data={'query': query})
    response = json.loads(httpresponse.text)
    print('Fuseki Response:')
    print(response)
    return response

# Build the corresponding query based on the intent
def buildquery(course, topic, event, intent, question):
    coursedict = {}
    resp_dict = {}
    subject = ''
    number = ''
    query=''
    answer='' 
    runquery = True

    if course != "NA":
        coursedict = course2dict(course)
        subject = coursedict['subject']
        number = coursedict['number']

    
    if topic != "NA":
        topicURI = topic2URI(topic)

    if intent == 'about_course':
        query = QUERY1%(subject,number)
        response = request2dict(query)
        headers = response['head']['vars']
        answer = course.upper() + " has "
        for header in headers:
            answer = answer + header + " " + response['results']['bindings'][0][header]['value'] + ", "

    elif intent == 'about_outline':
        query = QUERY12%(subject,number)
        response = request2dict(query)
        headers = response['head']['vars']
        answer = 'Course outline: %s'%response['results']['bindings'][0]['outline']['value'] 
        
    elif intent == 'about_course_number':
        query = QUERY4
        response = request2dict(query)
        answer = 'There are %s courses'%response['results']['bindings'][0]['CourseCount']['value'] 

    elif intent == 'about_course_reading':
        query = QUERY5%(subject,number)
        response = request2dict(query)
        results = response['results']['bindings'] 
        for result in results:
            answer = answer+"Lecture: "+ result['number']['value'] + " " + result['source']['value']+'\n'

    elif intent == 'about_same':
        answer = "Potential implementation for further questions"

    elif intent == 'about_subject':
        query = QUERY14%(subject)
        response = request2dict(query)
        results = response['results']['bindings'] 
        for result in results:
            answer = answer+"Course: "+ result['courseName']['value'] + " " + result['title']['value']+'\n'

    elif intent == 'about_course_content':
        query = QUERY6%(subject,number)
        response = request2dict(query)
        headers = response['head']['vars']
        answer = "Content for each lecture of " + course.upper() + ":\n" 
        results = response['results']['bindings']
        for result in results:
            for header in headers:
                answer = answer + header + ": " + result[header]['value'] + " "
            answer = answer + "\n" 

    elif intent == 'about_lecture_topics':
        if event != "NA":
            event_dict = event2dict(event)
            query = QUERY10%(subject,number,event_dict['event'], event_dict['event_number'])
            response = request2dict(query)
            headers = response['head']['vars']
            answer = "Topics covered in" + course.upper() + ":\n" 
            results = response['results']['bindings']
            for result in results:
                for header in headers:
                    answer = answer + header + ": " + result[header]['value'] + " "
                answer = answer + "\n" 
        else:
            query = QUERY2%(subject,number)
            response = request2dict(query)
            headers = response['head']['vars']
            answer = "Topics covered in" + course.upper() + ":\n" 
            results = response['results']['bindings']
            for result in results:
                for header in headers:
                    answer = answer + header + ": " + result[header]['value'] + " "
                answer = answer + "\n" 

    elif intent == 'about_event':
        event_dict = event2dict(event)
        query = QUERY9%(subject,number,event_dict['event'])
        response = request2dict(query)
        if response['boolean']:
            answer = 'Yes'
        else:
            answer = "No"

    elif intent == 'about_lecture_by_topic':
        #topic_uri = topic2URI(topic)
        topic_uri = topic2URI(question)
        if topic_uri != '':
            query = QUERY3%(subject,number,topic_uri)
            response = request2dict(query)
            headers = response['head']['vars']
            results = response['results']['bindings']
            answer = "Topic " + topic + " is covered in lectures "
            for result in results:
                for header in headers:
                    answer = answer + " " + result[header]['value']
                answer = answer + "," 
        else:
            answer = "No lecture found"
    elif intent == 'about_course_by_topic':
        #topic_uri = topic2URI(topic)
        topic_uri = topic2URI(question)
        if topic_uri != '':
            query = QUERY11%(topic_uri, topic_uri)
            response = request2dict(query)
            headers = response['head']['vars']
            results = response['results']['bindings']
            answer = "Topic: " + topic + " is covered in "
            for result in results:
                for header in headers:
                    answer = answer + " " + result[header]['value']
                answer = answer + "," 
        else:
            answer = "No course found"
    else:
        print("No query to process")
        runquery = False

    return answer

# Class to perform the corresponding action
class ActionCourseQuery(Action):

    def name(self) -> Text:
        return "action_course_query"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course']
        topic = tracker.slots['topic']
        event = tracker.slots['event']
        intent  = tracker.latest_message['intent'].get('name')
        question = tracker.latest_message['text']

        print(course)
        print(intent) 
        print(topic)
        print(event)
        print(question)

        resp = buildquery(course, topic, event, intent, question)

        #dispatcher.utter_message(text=f"You are asking about {tracker.slots['course']}: ")
        dispatcher.utter_message(text=f"{resp}")

        return []