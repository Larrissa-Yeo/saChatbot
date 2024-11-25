from flask import Flask, render_template, request, jsonify
from chatbot import Chat, register_call
import os
import random
import re
import pandas as pd

#app.py
#import files
app = Flask(__name__)

# Fallback responses
fallback_responses = [
    "I'm not sure how to answer that, but let's keep chatting!",
    "That's an interesting question. I'll need to think about it more.",
    "Hmm, I don't know about that. Can you ask something else?",
]

## Using a sample response template
# chat_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Example.template")
# chat = Chat(chat_template)

@app.route("/")
def home():
    
    return render_template("index.html")

tatics = [{"ID":"TA0043","Name":"Reconnaissance", "Description":"The adversary is trying to gather information they can use to plan future operations."},
          {"ID":"TA0042", "Name":"Resource Development", "Description":"The adversary is trying to establish resources they can use to support operations."},
          {"ID":"TA0001", "Name":"Initial Access", "Description":"The adversary is trying to get into your network."},
          {"ID":"TA0002", "Name":"Execution", "Description":"The adversary is trying to run malicious code."},
          {"ID":"TA0003", "Name":"Persistence", "Description":"The adversary is trying to maintain their foothold."},
          {"ID":"TA0004", "Name":"Privilege Escalation", "Description":"The adversary is trying to gain higher-level permissions."},
          {"ID":"TA0005", "Name":"Defense Evasion", "Description":"The adversary is trying to avoid being detected."},
          {"ID":"TA0006", "Name":"Credential Access", "Description":"The adversary is trying to steal account names and passwords."},
          {"ID":"TA0007", "Name":"Discovery", "Description":"The adversary is trying to figure out your environment."},
          {"ID":"TA0008", "Name":"Lateral Movement", "Description":"The adversary is trying to move through your environment."},
          {"ID":"TA0009", "Name":"Collection", "Description":"The adversary is trying to gather data of interest to their goal."},
          {"ID":"TA0011", "Name":"Command and Control", "Description":"The adversary is trying to communicate with compromised systems to control them."},
          {"ID":"TA0010", "Name":"Exfiltration", "Description":"The adversary is trying to steal data."},
          {"ID":"TA0040", "Name":"Impact", "Description":"The adversary is trying to manipulate, interrupt, or destroy your systems and data."}
          ]

def queryFilter(query):
    if query[0:2] == "TA" and (len(query)>4 and len(query)<8):
        searchCata = "technique tactics"
        return searchCata
    elif query[0] == "T" and (len(query)>4 and len(query)<10):
        searchCata = "technique ID"
        return searchCata
    elif query[0:3] == "APT" and query[3] == '-':
        searchCata = "group name"
        return searchCata
    elif query[0] == "G" and len(query) < 6:
        searchCata = "group ID"
        return searchCata
    else:
        for tatic in tatics:
            if tatic['Name'] == query:
                searchCata = "technique tactics"
                return searchCata
        searchCata = "technique name"
        return searchCata
        

# Extract query from user message
def extract_query(user_message):
    patterns = [
        r"what is (?P<query>.+)",
        r"who is (?P<query>.+)",
        r"tell me about (?P<query>.+)",
        r"do you know about (?P<query>.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            return match.group("query").strip()
    
    ### Michelle's Extract Query codes
    # technique_id_pattern = r"\b(T\d{4})\b"
    # technique_name_pattern = r"describe (?P<technique_name>.+)"

    # if match := re.search(technique_id_pattern, user_message, re.IGNORECASE):
    #     return {"type": "technique_id", "query": match.group(1)}

    # if match := re.search(technique_name_pattern, user_message, re.IGNORECASE):
    #     return {"type": "technique_name", "query": match.group("technique_name").strip()}

    # return {"type": "unknown", "query": user_message.strip()}
    # If no pattern matches, return the original message
    return user_message.strip()

data_csv = "updated_aptgroup_relationships.csv"

# ## Michelle generic response
# def generate_generic_response(query_info):
#     try:
#         # Load the CSV file
#         data = pd.read_csv(data_csv)

#         # Define the columns to search
#         search_columns = ["technique ID", "technique name", "group name", "technique description"]

#         if query_info["type"] == "technique_id":
#             # Search by technique ID
#             match = data[data["technique ID"].str.contains(query_info["query"], case=False, na=False)]
#             if not match.empty:
#                 result = match.iloc[0]
#                 return f"{result['technique ID']} is {result['technique name']} used by {result['group name']}."

#         elif query_info["type"] == "technique_name":
#             # Search by technique name
#             match = data[data["technique name"].str.contains(query_info["query"], case=False, na=False)]
#             if not match.empty:
#                 result = match.iloc[0]
#                 return f"{result['technique description']}"

#         # If no match is found
#         return f"Sorry, I couldn't find information about '{query_info['query']}'."

#     except Exception as e:
#         return f"An error occurred while processing your query: {str(e)}"

# Generic response generator
def generate_generic_response(query, searchCata):
    try:
        # Load the CSV file
        data = pd.read_csv(data_csv)

        # Define the columns to search for the query
        search_columns = ["group ID", "group name", "technique ID", "technique name", 
                          "group mapping description", "technique description", 
                          "technique tactics", "technique platforms", 
                          "is sub-technique of target", "target sub-technique of", 
                          "technique supports remote"]
        print(searchCata)
        if searchCata != None:
            print(searchCata)
            search_columns = search_columns
    
        match = data[
            data[search_columns].apply(
                lambda row: any(row.astype(str).str.contains(query, case=False, na=False)), axis=1
            )
        ]    

        # If a match is found, format the response
        if not match.empty:
            result = match.iloc[0]  # Get the first match
            if searchCata == "technique ID":
                response = (

                f"**Technique Details**<br>"
                f"----------------------<br>"
                f"Technique ID: {result['technique ID']}<br>"
                f"Technique Name: {result['technique name']}<br>"
                f"Technique Description:<br>{result['technique description']}<br><br>"

                f"**APT Group Information**<br>"
                f"-------------------------<br>"
                f"Group ID: {result['group ID']}<br>"
                f"Group Name: {result['group name']}<br><br>"

                f"**Additional Information**<br>"
                f"---------------------------<br>" 
                f"Group Mapping Description: {result['group mapping description']}<br>"
                f"Technique Tactics: {result['technique tactics']}<br>"
                f"Technique Platforms: {result['technique platforms']}<br>"
                f"Is Sub-Technique of Target: {result['is sub-technique of target']}<br>"
                f"Target Sub-Technique Of: {result['target sub-technique of']}<br>"
                f"Technique Supports Remote: {result['technique supports remote']}<br>"
                )

                return response
            elif searchCata == "group name" or search_columns == "group ID":
                response = (

                f"**APT Group Information**<br>"
                f"-------------------------<br>"
                f"Group ID: {result['group ID']}<br>"
                f"Group Name: {result['group name']}<br><br>"

                f"---------------------------<br>" 
                f"Group Mapping Description: {result['group mapping description']}<br>"
                f"Technique Tactics: {result['technique tactics']}<br>"
                f"Technique Platforms: {result['technique platforms']}<br>"
                f"Is Sub-Technique of Target: {result['is sub-technique of target']}<br>"
                f"Target Sub-Technique Of: {result['target sub-technique of']}<br>"
                f"Technique Supports Remote: {result['technique supports remote']}<br>"
                )

                return response
            elif searchCata == "technique tactics":
                for tatic in tatics:
                    print(tatic)
                    if tatic["ID"] == query or tatic['Name'] == query:
                        response = (
                        f"Tatic: {tatic['Name']}<br>"
                        f"Tatic ID: {tatic['ID']}<br>"
                        f"Tatic Description: {tatic['Description']}<br>"
                        )

                        return response
            elif searchCata == "technique name":
                response = (

                    f"Technique ID: {result['technique ID']}<br>"
                    f"Technique Name: {result['technique name']}<br><br>"
                    f"Technique Description:<br>{result['technique description']}<br><br>"

                    f"**APT Group Information**<br>"
                    f"-------------------------<br>"
                    f"Group ID: {result['group ID']}<br>"
                    f"Group Name: {result['group name']}<br><br>"

                    f"**Additional Information**<br>"
                    f"---------------------------<br>"
                    f"Group Mapping Description: {result['group mapping description']}<br>"
                    f"Technique Tactics: {result['technique tactics']}<br>"
                    f"Technique Platforms: {result['technique platforms']}<br>"
                    f"Is Sub-Technique of Target: {result['is sub-technique of target']}<br>"
                    f"Target Sub-Technique Of: {result['target sub-technique of']}<br>"
                    f"Technique Supports Remote: {result['technique supports remote']}<br>" 
                )
                return response



        # If no match is found, return a generic message
        return f"Sorry, I couldn't find information about '{query}'."

    except Exception as e:
        return f"An error occurred while processing your query: {str(e)}"

@app.route('/chat', methods=['POST'])
def chat_with_bot():
    user_message = request.json.get('message', "").strip()
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Extract the query from the user's message
        query = extract_query(user_message)

        searchCata = queryFilter(query)
        
        # Get the chatbot's response
        bot_response = generate_generic_response(query, searchCata)

        # If no response is found, return a random fallback response
        if not bot_response:
            bot_response = random.choice(fallback_responses)

        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
  app.run(debug=True)