from transformers import AutoTokenizer, AutoModelForSequenceClassification
from matplotlib import pyplot as plt
import firebase_admin
from firebase_admin import credentials, firestore
import openai
import torch
import torch.nn.functional as F
import random

# from nltk.corpus import stopwords

tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
model = AutoModelForSequenceClassification.from_pretrained("SamLowe/roberta-base-go_emotions")

# nltk_words = list(stopwords.words('english'))

openai.api_key = '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'

cred = credentials.Certificate('data.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


def getEmotions(input_text):
    # toList = input_text.split()
    #
    # for word in toList:
    #     if word in nltk_words:
    #         toList.remove(word)
    #
    # filtered = ' '.join(toList)

    input_ids = tokenizer.encode(input_text, add_special_tokens=True)

    attention_mask = [1] * len(input_ids)

    input_ids = torch.tensor([input_ids])
    attention_mask = torch.tensor([attention_mask])

    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    logits = outputs.logits

    probabilities = F.softmax(logits, dim=1)

    emotion_labels = [
        "admiration",
        "amusement",
        "anger",
        "annoyance",
        "approval",
        "caring",
        "confusion",
        "curiosity",
        "desire",
        "disappointment",
        "disapproval",
        "disgust",
        "embarrassment",
        "excitement",
        "fear",
        "gratitude",
        "grief",
        "joy",
        "love",
        "nervousness",
        "optimism",
        "pride",
        "realization",
        "relief",
        "remorse",
        "sadness",
        "surprise",
        "neutral"
    ]

    probabilities = probabilities.squeeze().detach().numpy().tolist()

    maxes = {}

    for x in range(0, 3):
        mx = max(probabilities)
        indmx = probabilities.index(mx)

        maxes[emotion_labels[indmx]] = mx
        emotion_labels.pop(indmx)
        probabilities.pop(indmx)

    return maxes


print(getEmotions('i am having a very good day'))


def getQuestions(input_text):
    prompt = f'''
    prompt: "Journal entry: {input_text}"

    I am currently writing a journal and want to write about this prompt topic.

    Ask me three questions about him that will guide my writing process.

    Write your questions as if you were asking me.

    '''

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=500,
        stop=None,
    )

    generated_response = response.choices[0].text.strip()

    return generated_response.strip("").split("\n")


def getTopic(input_text):
    topic = f'''
    prompt: "{input_text}"

    I am currently writing a journal and want to write about this prompt topic.

    What is the topic of the prompt that it provided, only return the topic in a couple of words.

    '''

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=topic,
        max_tokens=500,
        stop=None,
    )

    generated_response = response.choices[0].text.strip()

    return generated_response.strip("").split("\n")


def totalStats(doc_id):
    posts = db.collection(u'user-data').document(doc_id).get()
    totals = {}
    appeared = {}

    data = posts.to_dict()

    entries = data['Entries']

    for entry in entries['Entries']:

        for mood in entry['Moods']:

            if mood not in totals:

                totals[mood] = entry['Moods'][mood]
                appeared[mood] = 1

            else:
                appeared[mood] += 1

                current = totals[mood]
                sum = current * (appeared[mood] - 1) + entry['Moods'][mood]

                totals[mood] = sum / appeared[mood]

    return totals


# FIRESTORE METHODS
def postEntry(doc_id,text,emotions, title):
    posts = db.collection(u'user-data').document(doc_id).get()
    data = " "

    data = posts.to_dict()


    entries = data['Entries']['Entries']


    entries.append(
        {
            'Date': f'{title}',
            'Text':text,
            'Entry Number':len(entries) + 1,
            'Moods':emotions
        }
    )


    data['Entries'] = entries

    posts = db.collection(u'user-data').document(doc_id).get()


    doc = db.collection(u'user-data').document(posts.id)
    field_updates = {"Entries": data}
    doc.update(field_updates)


def getEntries(id):
    doc_ref = db.collection(u'user-data').document(id)

    doc_snapshot = doc_ref.get()

    doc_data = doc_snapshot.to_dict()

    return doc_data['Entries']['Entries']


def createUser(name,userID):


    obj1 = {
        'Entries': [
        ]
    }

    obj2 = {
        'Name': name,
        'Entries':obj1
    }

    data = [obj2]

    for record in data:
        doc_ref = db.collection(u'user-data').document(userID)
        doc_ref.set(record)


def plotPie(labels, data):
    colors = ['#88ddda', '#68FAEA', '#93FBEF']
    fig = plt.figure(figsize=(10, 7))
    patches, texts, autotexts = plt.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', counterclock=False)

    for text in texts:
        text.set_color('grey')

    fig.savefig('./static/img/pie.png', transparent=True)


def getName(doc_id):
    db = firestore.client()

    doc_ref = db.collection('user-data').document(doc_id)
    doc = doc_ref.get()

    return doc.to_dict()['Name']

# emotions = getEmotions(input_text)
# plotPie(emotions.keys(),emotions.values(),colors)
