import json


class WikiBase:

    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    TEST = "test.json"

    # tesing purpose
    @staticmethod
    def dumpResult(data):
        try:
            with open(WikiBase.TEST, "w") as f:
                json.dump(data, f)

        except Exception as e:
            print("Error")
