## Configuring Rasa

# Step 1 - Create a new intent in "data/nlu.yml"
E.g. 
- intent: query_course
  examples: |
    - what is [COMP 6741](course) about?
    - Which topics are covered in [LAB#2](event) of [COMP 6741](course)?
    - which coursers cover [Expert Systems](topic)?
    <!-- 10 Comptency questions -->
    - What is the course title and description of [COMP 6741](course)?
    - Which topics are covered in [COMP 6741](course) lectures?
    - Which lecture of [COMP 6741](course) covers [knowledge base](topic)?
    - How many courses are offered at Concordia University?
    - What are the recommended reading materials for [COMP 6741](course)?
    - What are the contents in [COMP 6741](course) for each lecture?
    - Does [COMP 6741](course) and [COMP 6731](course) cover similar topic?
    - What is the outline for [COMP 6741](course) ?
    - Which courses cover [knowledge_base](topic)?
    - Does [COMP 6741] has [LAB](event)?


# Step 2 - After creating intendt, update "domain.yml" with intent
intents:
  - greet
  - goodbye
  - affirm
  - deny
  - mood_great
  - mood_unhappy
  - bot_challenge
  - about_person
  - query_course

# Step 3 - Register entities in the same "domain.yml" file
entities:
  - person
  - course
  - event
  - topic

# Step 4 - Define the entity type in the slots section of "domain.yml"
slots:
  person:
    type: any
    initial_value: "initial"
  course:
    type: text
    initial_value: "initial"
  topic:
    type: text
    initial_value: "initial"
  event:
    type: text
    initial_value: "initial"



# Step 5 - Register action in the "domain.yml" file
actions:
  - action_person_info
  - action_course_query

# Step 6 - Create a story for how user will interact with system by updating "data/stories.yml"
- story: get course info
  steps:
    - intent: greet
    - action: utter_greet
    - intent: query_course
    - action: course_query

# Step 7 - Ensure following line is uncommented un "endpoints.yml"
action_endpoint:
url: "http://localhost:5055/webhook"

# Step 8 - Compile un run
    1. Navigate to main folder where all the rasa project and open 2 consoles
    2. In first console, to train the model type
        rasa train
        rasa shell
    3. In second console run
        rasa run actions