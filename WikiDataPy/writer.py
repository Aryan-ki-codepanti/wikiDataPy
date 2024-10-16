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

    def addClaim(self, entity_id, property_id, value_id):
        """
        Create a new claim on a Wikidata entity.

        :param entity_id: str, the ID of the entity (e.g., "Q42")
        :param property_id: str, the property ID (e.g., "P31")
        :param value_id: str, the ID of the value (e.g., "Q5")
        """

        if not self.csrf_token:
            print("You have no CSRF token, kindly login and then call getCSRFToken()")
            return

        params = {
            "action": "wbcreateclaim",
            "format": "json",
            "entity": entity_id,
            "snaktype": "value",
            "property": property_id,
            "value": json.dumps({
                "entity-type": "item",
                "numeric-id": int(value_id[1:])
            }),
            "token": self.csrf_token
        }

        # Send POST request to create the claim
        response = self.session.post(
            WikiWriter.API_ENDPOINT, data=params).json()

        # Handle errors
        if "error" in response:
            print("Error in creating claim:", response["error"])
            return response["error"]

        print("Claim created successfully:", response)
        return response

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


def write_test(w):
    # create / edit entity

    labels = {
        "en": "New Sample Entity by Aryan",
        "fr": "Nouvel exemple d'entité par Aryan"
    }
    descriptions = {
        "en": "This is a newly created sample entity by Aryan",
        "fr": "Il s'agit d'un exemple d'entité nouvellement créé par Aryan"
    }
    res = w.createOrEditEntity(labels=labels, descriptions=descriptions)
    WikiWriter.dumpResult(res, "test_createEntity.json")


def claim_test(w: WikiWriter):
    # create / edit claim
    e = "Q130532046"
    p = "P31"  # instance of
    v = "Q5"  # human
    res = w.addClaim(e, p, v)
    WikiWriter.dumpResult(res, "test_addClaim.json")


if __name__ == "__main__":
    w = WikiWriter(os.getenv("WIKI_USERNAME"), os.getenv("WIKI_PASSWORD"))

    w.login()
    w.getCSRFTtoken()

    # write test
    # write_test(w)

    # add claim test
    claim_test(w)

    w.logout()