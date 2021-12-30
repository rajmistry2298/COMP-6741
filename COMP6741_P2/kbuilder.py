from rdflib import Graph, Literal, Namespace, RDFS, URIRef, Literal
from rdflib.namespace import RDF, FOAF, DC, DCTERMS, Namespace, NamespaceManager #rdflib.namespace comes with predefined namespace
import pandas
from uuid import uuid4

UNI =  Namespace("http://uni.io/schema#")
UNIDATA = Namespace("http://uni.io/data#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/") 
DCMITYPE = Namespace("http://purl.org/dc/dcmitype/")
LOCAL = Namespace("http://localhost:3030")


def add_documents(location, type):
    contenId = UNIDATA["c" + str(uuid4())]
    graph.add((contenId, RDF.type, DCTERMS.BibliographicResource))
    graph.add((contenId, DCTERMS.type, Literal(type)))
    #graph.add((contenId, DCTERMS.source, URIRef(location)))
    if 'http' in location:
        graph.add((contenId, DCTERMS.source, URIRef(location)))
    else:
        graph.add((contenId, DCTERMS.source, LOCAL[location]))

    return contenId

#def add_lectures(course):

#>>> exNs = Namespace('http://example.com/')
namespace_manager = NamespaceManager(Graph())
namespace_manager.bind('UNI', UNI, override=False)  

graph = Graph()
graph.bind('DC', DC)

#Add Univeristy to graph
graph.add( (URIRef(UNIDATA.Concordia_University), RDF.type , UNI.University))
graph.add( (URIRef(UNIDATA.Concordia_University), DCTERMS.title , Literal("Concordia University", lang="en")))
graph.add( (URIRef(UNIDATA.Concordia_University), RDFS.seeAlso, DBR.Concordia_University))

#Read csv data
course_data = pandas.read_csv('datasets/course_data.csv')
lecture_data = pandas.read_csv('datasets/lecture_data.csv')
content_data = pandas.read_csv('datasets/content_data.csv')
lab_content_data = pandas.read_csv('datasets/lab_content_data.csv')
event_data = pandas.read_csv('datasets/event_data.csv')
topics_data = pandas.read_csv('datasets/topics.csv', encoding='latin-1')
lab_topics_data = pandas.read_csv('datasets/lab_topics.csv', encoding='latin-1')

#Add data to graph
for courseline in range(len(course_data)):
    course = course_data.iloc[courseline]

    courseId = UNIDATA[str(course['CourseId'])]
    graph.add((courseId, RDF.type, UNI.Course))
    graph.add((courseId, DCTERMS.title, Literal(str(course['Title']), lang="en")))
    graph.add((courseId, DCMITYPE.subject, Literal(str(course['Subject']))))
    graph.add((courseId, DCMITYPE.identifier, Literal(str(course['Number']))))
    graph.add((courseId, DCTERMS.description, Literal(str(course['Description']), lang="en")))
    if not pandas.isnull(course['seeAlso']):
        graph.add((courseId, RDFS.seeAlso, Literal((course['seeAlso']))))
        #graph.add((courseId, RDFS.seeAlso, URIRef(course['seeAlso'])))
    graph.add((courseId, UNI.topic, DBR[str(course['Topic'])]))
    graph.add((courseId, DCTERMS.isPartOf, UNIDATA.Concordia_University))
    if not pandas.isnull(course['Outline']):
        contentId = add_documents(course["Outline"],"OUTLINE")
        graph.add((courseId, UNI.hasContent, contentId))

    #For each course, add lectures
    courseLectures = lecture_data[lecture_data['CourseId'] == course['CourseId']]
    for lectureline in range(len(courseLectures)):
        lecture = courseLectures.iloc[lectureline]
        lectureId = UNIDATA["l" + str(uuid4())]
        graph.add((lectureId, RDF.type, UNI.Lecture))
        graph.add((lectureId, DCMITYPE.identifier, Literal(str(lecture['Identifier']))))
        graph.add((lectureId, DCTERMS.title, Literal(str(lecture['Title']))))
        graph.add((lectureId, RDFS.seeAlso, URIRef(lecture['seeAlso'])))
        #graph.add((lectureId, UNI.topic, DBR[str(lecture['Topic'])]))
        graph.add((lectureId, DCTERMS.isPartOf, courseId))
        
        #Content associated withe a lecture
        lectureContents = content_data[(content_data['CourseId'] == course['CourseId']) & (content_data['Identifier'] == lecture['Identifier'])]
        for contentline in range(len(lectureContents)):
            content = lectureContents.iloc[contentline]
            contentId = add_documents(content["Content"],content["ContentType"])
            graph.add((lectureId, UNI.hasContent, contentId))
        
        #Add topics generated using spotlight
        lectureTopics = topics_data[(topics_data['CourseId'] == course['CourseId']) & (topics_data['Identifier'] == lecture['Identifier'])]
        for topicline in range(len(lectureTopics)):
            topic = lectureTopics.iloc[topicline]
            graph.add((lectureId, UNI.topic, URIRef(str(topic['Link']))))

        #Events (labs/tutorials) associated with a lecture
        lectureEvents = event_data[(event_data['CourseId'] == course['CourseId']) & (event_data['Identifier'] == lecture['Identifier'])]
        
        for eventline in range(len(lectureEvents)): 
            event = lectureEvents.iloc[eventline]
            eventId = UNIDATA["e" + str(uuid4())]
            graph.add((eventId, RDF.type, UNI.Event))
            graph.add((eventId, DCTERMS.type, Literal(event["Event"])))
            #graph.add((eventId, UNI.topic, DBR[str(event['Topic'])]))
            graph.add((eventId, DCTERMS.isPartOf, lectureId))
            graph.add((eventId, DCMITYPE.identifier, Literal(lecture['Identifier'])))
            labTopics = lab_topics_data[(lab_topics_data['CourseId'] == course['CourseId']) & (lab_topics_data['Identifier'] == lecture['Identifier'])]
            for topicline in range(len(labTopics)):
                topic = labTopics.iloc[topicline]
                graph.add((eventId, UNI.topic, URIRef(str(topic['Link']))))
            
            #Content associated withe a lab
            labContents = lab_content_data[(lab_content_data['CourseId'] == course['CourseId']) & (lab_content_data['Identifier'] == lecture['Identifier'])]
            for contentline in range(len(labContents)):
                content = labContents.iloc[contentline]
                contentId = add_documents(content["Content"],content["ContentType"])
                graph.add((eventId, UNI.hasContent, contentId))

#Save data in N-Triple format
graph.serialize('Knowdlegde_base.nt',format='nt')
graph.serialize('knowledgebase.ttl', format='turtle')