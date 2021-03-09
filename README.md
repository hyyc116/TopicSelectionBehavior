# TopicSelectionBehavior
Stat the basic attribute of author topic selection behavior, and explore the underlying mechanisms.

## Data
APS dataset, Available by sending email to APS.org for research purpose.

## Author Disambugation
Same Name, Same Institution, Same Abbreviation

## Processing
PACS code as the topic.

### Staitic Indicators

Independent indicators:

    1. Unique number of Topic.
    2. Number of papers under same topic, Mean, Max
    3. Diversity of topics.
    4. Persistance.

Dependent indicators:
   
    1. Productivity
    2. Hindex
    3. Total number of citations.
    4. etc.

### Dynamic Indicators

#### Topic sequence example:

    t1 t1 | t2 t1 t2 | t3 t3 t2 | t4 t4 | t5
          |          |          |       |
          ^          ^          ^       ^
        Topic Transition
    When New topics are selected.

#### Two indicators:

1. Transition Pos: the relative position in topic sequence.

exp: (2+5+8+10)/11

    Expectation:
    |     ---                _ _ _ 
    |    /   \              /     \
    |   /     \_ _ _ _ _ __/       \_ _ _ _
    | _/
    |__________________________________________

2. Transtion Direction: transt to more polular topic or less popular topic.

    Transition Direction = N(new topic) - N(old topic)

