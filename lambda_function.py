from __future__ import print_function
from pprint import pprint
from collections import OrderedDict
from itertools import izip, repeat

import csv
import re
import urllib2
import boto3

n = []
n_temp = []
common_count = 0
att2 = [[]]
saved_att = []
att_save_count = 0
att = ''
printhelp = ''
string = ''
m = []
url = ''
response = ''
readCSV = ''
metric = '0'

#Function to give response to Alexa.

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" + output + " </speak>"
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + str(output)
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" + reprompt_text + "</speak>"
            }
        },
        'shouldEndSession': should_end_session
    }


def build_speechlet_response2(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" + output + "</speak>"
        },
        'card': {
            'type': 'Standard',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + str(output)
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" + reprompt_text + "</speak>"
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def dialog_response(session_attributes, endsession):
    """  create a simple json response with card """
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': {
            'directives': [
                {
                    'type': 'Dialog.Delegate',
                    "updatedIntent": {
                        "name": "test",
                        "confirmationStatus": "NONE",
                        "slots": {
                            "my": {
                                "name": "my",
                                "confirmationStatus": "NONE"
                            },
                        }
                    }
                }
            ],
            'shouldEndSession': endsession
        }
    }


def dialog_response2(session_attributes, endsession):
    """  create a simple json response with card """
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Welcome to Searching, what variable you want to search in data?",
            },
            'directives': [
                {
                    'type': 'Dialog.ElicitSlot',
                    'slotToElicit': 'rc',
                    "updatedIntent": {
                        "name": "search",
                        "confirmationStatus": "NONE",
                        "slots": {
                            "rc": {
                                "name": "rc",
                                "value": "",
                                "confirmationStatus": "NONE"

                            },
                        }
                    }}
            ],
            'shouldEndSession': endsession
        }
    }


def dialog_response_ranges(session_attributes, endsession):
    """  create a simple json response with card """
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Attribute contains both numeric and string data, do you want to proceed further?",
            },
            'directives': [
                {
                    'type': 'Dialog.ConfirmSlot',
                    "slotToConfirm": "tc",
                    "updatedIntent": {
                        "name": "range",
                        "confirmationStatus": "NONE",
                        "slots": {
                            "tc": {
                                "name": "tc",
                                "value": string,
                                "confirmationStatus": "NONE"

                            },
                        }
                    },
                }
            ],
            'shouldEndSession': endsession
        }
    }


def dialog_response_att_store(session_attributes, endsession):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "The attribute " + str(att) + " has been added, do you want to add any other attribute?",
            },
            'directives': [
                {
                    'type': 'Dialog.ConfirmSlot',
                    "slotToConfirm": "att",
                    "updatedIntent": {
                        "name": "att_store",
                        "confirmationStatus": "NONE",
                        "slots": {
                            "att": {
                                "name": "att",
                                "value": att,
                                "confirmationStatus": "NONE"

                            },
                        }
                    }}
            ],
            'shouldEndSession': endsession
        }
    }


#Function to open .CSV data file.
def open_data(intent):
    try:
        global n
        n[:] = []
        global n_temp
        n_temp[:] = []
        global common_count
        common_count = 0
        global string
        string = intent['slots']['file']['value']
        global url
        url = 'https://s3.amazonaws.com/lawishbucket/' + string
        global response
        response = urllib2.urlopen(url)
        global readCSV
        readCSV = csv.reader(response)
        for row in readCSV:
            global m
            m.append(row)

        session_attributes = {}
        card_title = "open data file"
        speech_output = 'You are now ready to work with the data file'
        reprompt_text = "You never responded to the first test message. Sending another one."
        should_end_session = False
        global metric
        metric = '1'
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    except:
        session_attributes = {}
        card_title = "open data file"
        speech_output = 'File not found, please try again!'
        reprompt_text = "You never responded to the first test message. Sending another one."
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


def get_test_response(request, intent):
    session_attributes = {}
    card_title = "Test"
    speech_output = 'Hello again!! \n Welcome to the Database Search tool'
    reprompt_text = "You never responded to my previous message. Hello again!! \n Welcome to the Demo for Database Search tool"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#Searching data in database and storing it in an array

def search_data(request, intent):
    print("running")
    if 'dialogState' in request:
        if request['dialogState'] == "STARTED":
            session_attributes = {}
            print("running")
            return dialog_response2(session_attributes, False)
    global string
    string = intent['slots']['rc']['value']
    # string = string.upper()
    print(string)
    temp = 0
    again = csv.reader(response, delimiter=',')
    for row in m:
        for field in row:
            if field == string.capitalize() or field == string.upper():
                temp = temp + 1
        if temp == 0:
            out = "not found in data"
        if temp != 0:
            out = "There are total " + str(temp) + " number of entries with name " + string + " in data"

    session_attributes = {}
    card_title = "Search"
    speech_output = str(out)
    reprompt_text = "You never responded to my previous message. " + str(out)
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#Finding range of data i.e smalledt or biggest value

def ranges(request, intent):
    global string
    string = intent['slots']['tc']['value']
    count = 0
    count1 = 0
    m3 = []
    m2 = []
    pos = ''
    # print("done")
    for row in m:
        for field in row:
            if field == string.capitalize() or field == string.upper() and count == 0:
                count += 1;
                pos = row.index(field)
    count = 0
    count1 = 0
    for i in range(1, len(m)):
        m2.append(m[i][pos])
    for x in m2:
        if x.isdigit():
            m3.append(int(x));
            count1 += 1
        try:
            if isinstance(float(x), float):
                m3.append(float(x))
                count1 += 1
        except:
            if isinstance(x, basestring) and x != '':
                count += 1;
    if len(m3) != 0:
        out = "The range of the attribute is from " + str(min(m3)) + " to " + str(max(m3)) + "."
    if count1 > 0 and count > 0:
        if 'dialogState' in request:
            if request['dialogState'] == "STARTED":
                session_attributes = {}
                return dialog_response_ranges(session_attributes, False)
            if request['intent']['slots']['tc']['confirmationStatus'] == "CONFIRMED":
                out = "The range of the attribute is from " + str(min(m3)) + " to " + str(max(m3)) + "."
            if request['intent']['slots']['tc']['confirmationStatus'] == "DENIED":
                out = "User Declined! Please select other attribute."
    elif count > 0:
        out = "Attribute contains only strings, please select other attribute."

    count = 0
    session_attributes = {}
    card_title = "Range"
    speech_output = str(out)
    reprompt_text = "You never responded to my previous message. " + str(out)
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#Storing attributes which user wants to save for his data analytics.

def att_store(request, intent):
    try:
        if request['intent']['slots']['att']['confirmationStatus'] == "NONE":
            global att
            att = (intent['slots']['att']['value'])
            print(att)
            count = 0
            # A1 = []
            pos = ''
            checker = False
            print("done")
            print(checker)
            for s in saved_att:
                if s == att or s == att.upper() or s == att.capitalize():
                    checker = True
            print(checker)
            if not checker:
                for row in m:
                    for field in row:
                        if field == att.capitalize() or field == att.upper() and count == 0:
                            count += 1;
                            global saved_att
                            saved_att.append(field);
                            pos = row.index(field)
                            print("done2")
                if att_save_count > 0:
                    global att2
                    att2.append([])
            print(not checker)
            print(len(att2))
            print(saved_att)
            for i in range(0, len(m)):
                global att2
                att2[att_save_count].append(m[i][pos])
    except:
        pass
    if 'dialogState' in request:
        if request['dialogState'] == "STARTED":
            session_attributes = {}
            return dialog_response_att_store(session_attributes, False)
        if request['intent']['slots']['att']['confirmationStatus'] == "CONFIRMED":
            out = "To add more attributes to the list, say 'add {attribute name}'"
            global att_save_count
            att_save_count += 1
        if request['intent']['slots']['att']['confirmationStatus'] == "DENIED":
            out = "All the attributes are saved. To view the saved attributes say 'view saved attributes/stores attributes' "
    print(att2)
    session_attributes = {}
    card_title = "Adding Attribute"
    speech_output = str(out)
    reprompt_text = "You never responded to my previous message. " + str(out)
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#displaying saved attributes.

def view_saved_att():
    temp2 = (', '.join(saved_att))
    if att_save_count == 0:
        out = "There are currently no saved attributes in database"
    else:
        out = "There are total " + str(len(saved_att)) + " saved attributes in database, named - " + str(temp2)
    session_attributes = {}
    card_title = "View Attribute"
    speech_output = str(out)
    reprompt_text = "I don't know if you heard me, " + str(out)
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def row_matching():
    count = 0
    for i in range(0, len(m)):
        for row in m:
            if m[i] == row:
                count += 1
    if count <= 1:
        out = 'There is no matching row'
    elif count > 1:
        out = 'There is ' + str(count) + ' matching rows'
    print(count)
    session_attributes = {}
    card_title = "Row_Match"
    speech_output = str(out)
    reprompt_text = "You never responded to my previous message. " + str(out)
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def row_intersection():
    count = 0
    temp = []
    try:
        temp = set(m[1])
        for s in m[2:]:
            if s != ' ':
                temp.intersection_update(s)

    except:
        pass
    print(list(temp))

    if (len(temp) > 0):
        out = "There are " + str(len(temp)) + " common elements in data."
    else:
        out = "There is no common element"
    session_attributes = {}
    card_title = "Row_Match"
    speech_output = "Row intersection completed. " + str(out)
    reprompt_text = "You never responded to my previous message. Row intersection completed. " + str(out)
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def intersect_SavedAtt():
    count = 0
    temp = []
    try:
        if not att2[0]:
            out = "There are no saved attributes to intersect. Please add some attributes"
        else:
            temp = set(att2[0])
            for s in att2[1:]:
                temp.intersection_update(s)
    except:
        pass
    if not temp:
        out = "There is no common elements in attributes"
    else:
        out = "Saved Attributes intersection completed."
    len(att2[0])
    print(att2[0])
    print(list(temp))
    session_attributes = {}
    card_title = "Saved Att Intersection"
    speech_output = str(out)
    reprompt_text = "You never responded to my previous message." + str(out)
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def show_all_att():
    disp = (', '.join(list(m[0])))
    session_attributes = {}
    card_title = "display all attributes"
    speech_output = "The attributes in the data file are - " + str(disp)
    reprompt_text = "I don't know if you heard me, the attributes in the data file are - " + str(disp)
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def show_att(intent):
    try:
        new_temp = []
        count = 0
        temp2 = []
        a_count = 0
        s_att = [[]]
        satt_temp = (intent['slots']['satt']['value'])
        satt = satt_temp.encode('ascii', 'ignore')
        satt = re.split(", | ,|,| , ", satt)
        print("length of m = " + str(len(m)))
        print(len(satt))
        for i in range(0, len(satt)):
            for row in m:
                for field in row:
                    if field == satt[i].capitalize() or field == satt[i].upper() or field == satt[i] and count < len(
                            satt):
                        count += 1
                        pos = row.index(field)
                        print("done2")
            if a_count > 0:
                print("done3")
                s_att.append([])
            for i in range(0, len(m)):
                s_att[a_count].append(m[i][pos])
                count = + 1
            a_count += 1
        temp2 = [item for sublist in s_att for item in sublist]

        temp3 = list(OrderedDict(izip(temp2, repeat(None))))
        temp4 = ', '.join(temp3)
        out = temp3
        print(temp4)
    except:
        out = "Attribute does not exist"
    print(i)
    print("length of m = " + str(len(m)))
    print(a_count)
    session_attributes = {}
    card_title = "display attribute values"
    speech_output = str(out)
    reprompt_text = "I don't know if you heard me, is there anything else I can do for you?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#finding common in attributes data points and storing it

def find_common(intent):
    characters = 0
    disp = ''
    disp1 = ''
    try:
        j = 0
        common_element = intent['slots']['element']['value']
        string2 = common_element.encode('ascii', 'ignore')
        string2 = [x.strip() for x in string2.split(' in ')]
        if common_count > 0:
            for row in n:
                for field in row:
                    if field == string2[1].capitalize() or field == string2[1].upper() or field == string2[1]:
                        pos = row.index(field)
                        if j == 0:
                            j += 1
                            global n
                            n_temp.append(row)
                        for i in range(0, len(n)):
                            if string2[0].capitalize() == n[i][pos] or string2[0].upper() == n[i][pos] or string2[0] == n[i][pos]:
                                global n_temp
                                n_temp.append(n[i])
                                global common_count
                                common_count += 1
            global n
            n = []
            global n
            n = list(n_temp)
            disp = ''
            disp1 = ''
            for i in range(0, len(n)):
                disp1 += ' ---- ['
                disp = (', '.join(list(n[i])))
                disp1 += disp
                disp1 += '] '
            global n_temp
            n_temp = []
        else:
            j = 0
            disp = ''
            disp1 = ''
            global n
            n = []
            global n_temp
            n_temp = []
            for row in m:
                for field in row:
                    if field == string2[1].capitalize() or field == string2[1].upper() or field == string2[1]:
                        pos = row.index(field)
                        if j == 0:
                            j += 1
                            global n
                            n.append(row)
                        for i in range(0, len(m)):
                            if string2[0].capitalize() == m[i][pos] or string2[0].upper() == m[i][pos] or string2[0] == m[i][pos]:
                                global n
                                n.append(m[i])
                                global common_count
                                common_count += 1
        disp = ''
        disp1 = ''
        for i in range(0, len(n)):
            if i > 0:
                disp1 += '- - - - - - Row ' +str(i)+ ' =  ['
                disp = (', '.join(list(n[i])))
                disp1 += disp
                disp1 += '] '
            else:
                disp1 += '- - - - ['
                disp = (', '.join(list(n[i])))
                disp1 += disp
                disp1 += '] '
        out ="There are "+str(len(n)-1)+" rows filtered "+ str(disp1)
    except:
        out = "Invalid Input."

    for row in n:
        characters += (len(row) * 4)
        for field in row:
            characters += len(field)
    if len(n) <= 1:
        out = "There is no filtered rows."
    if characters > 5800:
        out = "There are total "+str(len(n)-1)+" rows filtered!! You can save data in file by saying save data in 'file name' or save 'file name'."
    session_attributes = {}
    card_title = "find common rows"
    speech_output = str(out)
    reprompt_text = "I don't know if you heard me, is there anything else I can do for you?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def save_data(intent):
    save_file = intent['slots']['file']['value']
    with open("/tmp/" + save_file + ".csv", 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for row in n:
            wr.writerow(row)
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('/tmp/' + save_file + ".csv", 'lawishbucket', save_file + ".csv")

    session_attributes = {}
    card_title = "Saving file"
    speech_output = "File saved."
    reprompt_text = "I don't know if you heard me, is there anything else I can do for you?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def find_prob():
    prob = 0
    if not n:
        out = "No data present."
    else:
        print(m)
        print(len(m))
        prob = (len(n) - 1) / float((len(m) - 1))
        prob = str(round(prob, 3))
        out = "Probabiblity comes out to be " + str(len(n) - 1) + "/" + str(len(m) - 1) + " that is " + str((prob))
    session_attributes = {}
    card_title = "Welcome"
    speech_output = str(out)
    reprompt_text = "I don't know if you heard me, welcome to the Demo for Database Search tool."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def clear_all():
    global n
    n = []
    global n_temp
    n_temp = []
    global common_count
    common_count = 0
    session_attributes = {}
    card_title = "Delete all"
    speech_output = "All Data Deleted."
    reprompt_text = "I don't know if you heard me, welcome to the Demo for Database Search tool."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_welcome_response():
    global metric
    metric = '0'
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi! Welcome to the Database Search tool."
    reprompt_text = "I don't know if you heard me, welcome to the Demo for Database Search tool."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_next_step():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Is there anything else I can do for you?"
    reprompt_text = "I don't know if you heard me, is there anything else I can do for you?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = 'Thank you for trying the Alexa Skills.'
    # "Have a nice day! "
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Events ------------------


def on_session_started(session_started_request, session):
    pass


def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    if intent_name == "open_file":
        return open_data(intent)
    if intent_name == "test":
        return get_test_response(intent_request, intent)
    if intent_name == "next_step":
        return get_next_step()
    if metric == '1':
        if intent_name == "search":
            return search_data(intent_request, intent)
        if intent_name == "row_match":
            return row_matching()
        if intent_name == "range":
            return ranges(intent_request, intent)
        if intent_name == "att_store":
            return att_store(intent_request, intent)
        if intent_name == "saved_att":
            return view_saved_att()
        if intent_name == "row_intersection":
            return row_intersection()
        if intent_name == "intersect_SavedAtt":
            return intersect_SavedAtt()
        if intent_name == "show_all_att":
            return show_all_att()
        if intent_name == "show_att":
            return show_att(intent)
        if intent_name == "find_common":
            for i in range(0, 2):
                return find_common(intent)
        if intent_name == "save_data":
            return save_data(intent)
        if intent_name == "find_prob":
            return find_prob()
        if intent_name == "clear_all":
            return clear_all()
        if intent_name == "AMAZON.HelpIntent":
            return get_welcome_response()
        if intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return handle_session_end_request()
        else:
            raise ValueError("Invalid intent")
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        global n
        n = []
        global n_temp
        n_temp = []
        session_attributes = {}
        card_title = "fallback"
        speech_output = "Try Again, There is no data file selected!"
        reprompt_text = "You never responded to the first test message. Sending another one."
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


def on_session_ended(session_ended_request, session):
    card_title = "Session Ended"
    speech_output = 'Thank you for trying the Alexa Skills Kit sample.'
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    print("Incoming request...")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])