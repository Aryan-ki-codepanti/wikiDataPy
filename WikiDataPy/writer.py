import requests
import os
from dotenv import load_dotenv
from BASE import WikiBase
import json
import pprint

load_dotenv()


class WikiWriter(WikiBase):

    API_ENDPOINT = "https://test.wikidata.org/w/api.php"

    def __init__(self, username: str, password: str):
        """
            Initialise writer object with login credentials\n 
            Recommended to use environment variables

            :param username: str, username of wikidata account
            :param password:  str, password of wikidata account

        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token = ""

    # auth

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

    def addClaim(self, entity_id: str, property_id: str, value_id: str):
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

    def removeClaims(self, claim_guids: list[str]):
        """
        Removes  claims by their guids.

        :param claim_guids: list[str], the list  of the guids size not more than 50
        """

        if not self.csrf_token:
            print("You have no CSRF token, kindly login and then call getCSRFToken()")
            return []

        if not type(claim_guids) != list[str] or len(claim_guids) > 50:
            print("Invalid input expected list of strings (max size 50)")
            return []

        params = {
            "action": "wbremoveclaims",
            "format": "json",
            "token": self.csrf_token,
            "claim": "|".join(claim_guids)
        }

        # Send POST request to create the claim
        response = self.session.post(
            WikiWriter.API_ENDPOINT, data=params).json()

        # Handle errors
        if "error" in response:
            print("Error in removing claims:", response["error"])
            return response["error"]

        print("Claims removed successfully:", response)
        return response

    def createOrEditEntity(self, labels: dict, descriptions: dict, aliases: dict = None, entity_id: str = None):
        '''
                options
                - labels
                - descriptions
                - aliases

                sample
                labels = {
                                "en": "New Sample Entity",
                                "fr": "Nouvelle Entité Exemple"
                        }
                descriptions = {
                                "en": "This is a newly created sample entity.",
                                "fr": "Ceci est une nouvelle entité exemple."
                        }

                aliases = {
                    "en": ["alias1","alias2"]
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

        if aliases:
            data["aliases"] = {x: [{"language": x, "value": i}
                                   for i in aliases[x]] for x in aliases}

        params["data"] = json.dumps(data)
        # sending post the request
        response = self.session.post(
            WikiWriter.API_ENDPOINT, data=params).json()

        if "error" in response:
            print("Error in creating or editing entity:", response["error"])
        else:
            print(f"Entity {action} successfully:", response)

        return response

    def delete_entity(self, entity_id: str):
        """
            *will work only your account has moderator status*\n
            Delete an entity on Wikidata by its ID.

            :param entity_id: str, the ID of the entity (e.g., "Q42")
            :return:  Response from the API, or error message if deletion fails.
        """
        params = {
            "action": "delete",
            "format": "json",
            "title": entity_id,
            "token": self.csrf_token
        }

        response = self.session.post(self.API_ENDPOINT, data=params).json()

        if "error" in response:
            print("Error in deleting entity:", response["error"])
            return response["error"]

        print("Entity deleted successfully:", entity_id)
        return response

    def setLabel(self, entity_id: str, language_code: str, label: str):
        """
        Create a new label or update existing label of entity (entity_id) having language_code
        with value label

        :param entity_id: str, the ID of the entity (e.g., "Q42")
        :param language_code: str, languagecode  (e.g., "hi" for hindi , "en" for english)
        :param label: str, the value of the label (e.g., "This is  a label")

        example:
            ent = "Q130532046"
            lang = "anp"  # hindi
            val = "मैं आर्यन हूं ha"

            data = w.setLabel(ent, lang, val)

        """
        if not self.csrf_token:
            print("You have no csrf token, kindly login and then call getCSRFToken()")
            return

        params = {
            "action": "wbsetlabel",
            "token": self.csrf_token,
            "format": "json",
            "id": entity_id,
            "language": language_code,
            "value": label
        }

        resp = self.session.post(WikiWriter.API_ENDPOINT, data=params).json()

        if "error" in resp:
            print("Error while setting label")
            print(resp["error"])
            return resp["error"]
        print("Label added successfully")
        return resp

    def setDescription(self, entity_id: str, language_code: str, description: str):
        """
        Create a new description or update existing description of entity (entity_id) having language_code
        with value description

        :param entity_id: str, the ID of the entity (e.g., "Q42")
        :param language_code: str, languagecode  (e.g., "hi" for hindi , "en" for english)
        :param description: str, the value of the description (e.g., "This is  a description")

        example:
            ent = "Q130532046"
            lang = "anp"  # hindi
            val = "मैं आर्यन हूं ha"

            data = w.setdescription(ent, lang, val)

        """
        if not self.csrf_token:
            print("You have no csrf token, kindly login and then call getCSRFToken()")
            return

        params = {
            "action": "wbsetdescription",
            "token": self.csrf_token,
            "format": "json",
            "id": entity_id,
            "language": language_code,
            "value": description
        }

        resp = self.session.post(WikiWriter.API_ENDPOINT, data=params).json()

        if "error" in resp:
            print("Error while setting Description")
            print(resp["error"])
            return resp["error"]
        print("Description added successfully")
        return resp

    def setAliases(self, entity_id: str, aliases: list[str], language_code: str = "en"):
        """
        Sets  aliase(s) of entity (entity_id) having language_code

        :param entity_id: str, the ID of the entity (e.g., "Q42")
        :param language_code: str, languagecode  (e.g., "hi" for hindi , "en" for english) default english
        :param aliases: str or list[str], the alias of list of aliases of the entity (e.g., "MyEntity" or ["E1","E2"])

        example:
            ent = "Q130532046"
            lang = "en"  # hindi
            val = "MyEntity_1"

            data = w.setAliases(ent, val,lang)

        """
        if not self.csrf_token:
            print("You have no csrf token, kindly login and then call getCSRFToken()")
            return

        aliases = aliases if type(aliases) == str else "|".join(aliases)

        params = {
            "action": "wbsetaliases",
            "token": self.csrf_token,
            "format": "json",
            "id": entity_id,
            "language": language_code,
            "set": aliases
        }

        resp = self.session.post(WikiWriter.API_ENDPOINT, data=params).json()

        if "error" in resp:
            print("Error while setting Aliases")
            print(resp["error"])
            return resp["error"]
        print("Aliases added successfully")
        return resp

    def addRemoveAliases(self, entity_id: str, add:  list[str] = "", remove: list[str] = "", language_code: str = "en"):
        """
        Sets  aliase(s) of entity (entity_id) having language_code

        :param entity_id: str, the ID of the entity (e.g., "Q42")
        :param add: str or list[str], the alias of list of aliases of the entity to be added (e.g., "MyEntity" or ["E1","E2"])
        :param remove: str or list[str], the alias of list of aliases of the entity to be removed (e.g., "MyEntity" or ["E1","E2"])
        :param language_code: str, languagecode  (e.g., "hi" for hindi , "en" for english) default english

        example:
            ent = "Q130532046"
            lang = "en"  # hindi
            add = ["E2","E1"]
            remove = ["MyEntity_1"]

            data = w.addRemoveAliases(ent, val,lang)

        """
        if not self.csrf_token:
            print("You have no csrf token, kindly login and then call getCSRFToken()")
            return

        add = add if type(add) == str else "|".join(add)
        remove = remove if type(remove) == str else "|".join(remove)

        params = {
            "action": "wbsetaliases",
            "token": self.csrf_token,
            "format": "json",
            "id": entity_id,
            "language": language_code
        }
        if add:
            params["add"] = add
        if remove:
            params["remove"] = remove

        resp = self.session.post(WikiWriter.API_ENDPOINT, data=params).json()

        if "error" in resp:
            print("Error while changing Aliases")
            print(resp["error"])
            return resp["error"]
        print("Aliases changed successfully")
        return resp


'''

Performing write/update  operations that require authentication , make sure to first login
'''

# create / edit entity


def write_test(w: WikiWriter):

    labels = {
        "en": "Sample 2 ",
        "fr": "Nouvel exemple d'entité par"
    }
    descriptions = {
        "en": "Sample tested desc 2",
        "fr": "Il s'agit d'un exemple d'entité nouvellement créé par "
    }

    aliases = {
        "en": ["alias1", "alias2"],
        "fr": ["aliase1", "aliase2"]
    }

    res = w.createOrEditEntity(
        labels=labels, descriptions=descriptions, aliases=aliases, entity_id="Q236479")


def add_claim_test(w: WikiWriter):
    # create / edit claim
    # test data
    e = "Q236479"
    p = "P98614"  # created my prop
    v = "Q19"
    # p = "P31"  # instance of
    # v = "Q5"  # human
    res = w.addClaim(e, p, v)
    pprint.pprint(res)


def remove_claim_test(w: WikiWriter):
    # create / edit claim
    guids = [
        "Q236560$84FD8F03-ADA8-46FA-A694-D4611A1D5DB2"
    ]

    res = w.removeClaims(guids)

    pprint.pprint(res)


def label_test(w: WikiWriter):

    ent = "Q236560"
    lang = "hi"  # hindi
    val = "मैं आर्यन हूं ha2987"

    data = w.setLabel(ent, lang, val)
    pprint.pprint(data)


def desc_test(w: WikiWriter):

    ent = "Q236560"
    lang = "hi"  # hindi
    val = "यह एक विवरण है विवरण20ohihs है विवरण है विवरण है"

    data = w.setDescription(ent, lang, val)
    pprint.pprint(data)


def set_alias_test(w: WikiWriter):

    ent = "Q236560"
    lang = "hi"
    val = ["उपनाम14", "उपनाम176"]

    data = w.setAliases(ent, val, lang)

    pprint.pprint(data)


def addRem_alias_test(w: WikiWriter):

    ent = "Q236479"
    lang = "en"
    add = ["E2", "E1"]
    remove = ["MyEntity_1"]

    data = w.addRemoveAliases(ent, add, remove, lang)
    pprint.pprint(data)


def delete_test(w: WikiWriter):
    e = "Q236479"
    data = w.delete_entity(e)
    pprint.pprint(data)


if __name__ == "__main__":
    w = WikiWriter(os.getenv("WIKI_USERNAME"), os.getenv("WIKI_PASSWORD"))

    w.login()
    w.getCSRFTtoken()

    # create / edit entity test
    # write_test(w)

    # 8 add claim test
    # add_claim_test(w)

    # 9 remove claims test
    # remove_claim_test(w)

    # 10 Label set test
    label_test(w)

    # 11 description set test
    desc_test(w)

    # 12 set alias test
    set_alias_test(w)

    # 13 add remove alias test
    # addRem_alias_test(w)

    # 14 DEL
    # delete_test(w)

    w.logout()
