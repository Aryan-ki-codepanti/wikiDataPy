import json


class WikiBase:

    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    TEST = "test.json"

    # tesing purpose
    @staticmethod
    def dumpResult(data, fname=None):
        try:
            fname = fname if fname else WikiBase.TEST
            with open(fname, "w") as f:
                json.dump(data, f)

        except Exception as e:
            print("Error")
