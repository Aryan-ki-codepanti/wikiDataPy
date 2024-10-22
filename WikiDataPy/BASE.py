import json


class WikiBase:

    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    TEST = "test.json"

    # testing purpose
    @staticmethod
    def dumpResult(data, fname=None):
        """
        Writes python object to json file

        :param data: python object to be written 
        :param fname: json path/file name 

        """

        try:
            fname = fname if fname else WikiBase.TEST
            with open(fname, "w") as f:
                json.dump(data, f)

        except Exception as e:
            print("Error")
