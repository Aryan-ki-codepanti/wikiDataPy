import requests
import os
from dotenv import load_dotenv
from BASE import WikiBase
import json
load_dotenv()


class WikiWriter(WikiBase):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token = ""

    def login(self):

        params = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }
        response = self.session.get(
            WikiWriter.API_ENDPOINT, params=params).json()
        login_token = response['query']['tokens']['logintoken']

        login_params = {
            "action": "clientlogin",
            "loginreturnurl": "https://www.wikidata.org",
            "logintoken": login_token,
            "username": self.username,
            "password": self.password,
            "format": "json"
        }

        login_response = self.session.post(
            WikiWriter.API_ENDPOINT, data=login_params).json()

        if login_response['clientlogin']['status'] == 'PASS':
            print("Successfully logged in.")
        else:
            print("Login failed:", login_response)

    def getCSRFTtoken(self):
        ''' Get CSRF token '''

        params = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }

        response = self.session.get(
            WikiWriter.API_ENDPOINT, params=params).json()

        self.csrf_token = response['query']['tokens']['csrftoken']

    def logout(self):
        """
            To logout from current session
        """
        params = {
            "action": "logout",
            "format": "json"
        }
        response = self.session.post(WikiWriter.API_ENDPOINT, data=params)

        if response.status_code == 200:
            print("Successfully logged out.")
        else:
            print("Error logging out:", response.text)

    # functionalities

    def addClaim():
        pass

    def createOrEditEntity(self, labels, descriptions, entity_id=None):
        '''
            options
            - labels
            - descriptions

            sample
            labels = {
                    "en": "New Sample Entity",
                    "fr": "Nouvelle Entité Exemple"
                }
            descriptions = {
                    "en": "This is a newly created sample entity.",
                    "fr": "Ceci est une nouvelle entité exemple."
                }

            - clear : erase then write labels , descriptions

            - provide id if you want to edit say Q150

        '''
        if not self.csrf_token:
            print("You have no csrf token, kindly login and then call getCSRFToken()")
            return

        # create new
        params = {

            "action": "wbeditentity",
            "token": self.csrf_token,
            "format": "json"

        }
        if entity_id is None:
            params["new"] = "item"
            action = "created"
        else:
            params["id"] = entity_id
            action = "updated"

        if not labels:
            print("Provide labels")
            return

        # Add labels
        data = {}
        data["labels"] = {lang: {"language": lang, "value": label}
                          for lang, label in labels.items()}

        # Add descriptions if provided
        if descriptions:
            data["descriptions"] = {
                lang: {"language": lang, "value": desc} for lang, desc in descriptions.items()}

        params["data"] = json.dumps(data)
        # sending post the request
        response = self.session.post(
            WikiWriter.API_ENDPOINT, data=params).json()

        if "error" in response:
            print("Error in creating or editing entity:", response["error"])
        else:
            print(f"Entity {action} successfully:", response)

        return response


'''

Performing write/update  operations that require authentication , make sure to first login
'''


if __name__ == "__main__":
    w = WikiWriter(os.getenv("WIKI_USERNAME"), os.getenv("WIKI_PASSWORD"))

    w.login()
    w.getCSRFTtoken()

    # write test
    labels = {
        "en": "New Sample Entity by Aryan",
        "fr": "Nouvel exemple d'entité par Aryan"
    }
    descriptions = {
        "en": "This is a newly created sample entity by Aryan",
        "fr": "Il s'agit d'un exemple d'entité nouvellement créé par Aryan"
    }
    res = w.createOrEditEntity(labels=labels, descriptions=descriptions)
    WikiWriter.dumpResult(res)

    w.logout()
