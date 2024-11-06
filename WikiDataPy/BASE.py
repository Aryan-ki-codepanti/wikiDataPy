import json
import csv


class WikiBase:

    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    TEST = "test.json"

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

    @staticmethod
    def dumpCSV(fname, head, data):
        """
        Writes python object to CSV file

        :param data: python object to be written 

        """

        try:
            with open(fname, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=head)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            print("Error while writing")
