import json
import csv
import os


class WikiBase:

    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    TEST = "test.json"

    @staticmethod
    def clear():
        """
            Clear terminal / console
        """
        # for windows
        if os.name == 'nt':
            _ = os.system('cls')

        # for mac and linux(here, os.name is 'posix')
        else:
            _ = os.system('clear')

    @staticmethod
    def dumpResult(data: object, fname=None):
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
    def dumpCSV(fname: str, head: list[str], data: list):
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

    @staticmethod
    def convertToCSVForm(data: dict, lang=["en"], gloss=False):
        """
            gloss boolean controls wether gloss field included or not
        """
        try:
            dt = []
            hdr = ['id']  # then glosses label description in langs

            for l in lang:
                h1 = [f'label-{l}', f'description-{l}']
                if gloss:
                    h1.append(f'gloss-{l}')
                hdr.extend(h1)

            for queryRes in data:
                ent = data[queryRes]
                rec = {}
                rec['id'] = ent['id']
                # for keys in ['labels','descriptions','glosses']
                for l in lang:
                    rec[f'label-{l}'] = rec[f'description-{l}'] = ''
                    if gloss:
                        rec[f'gloss-{l}'] = ''

                    if "labels" in ent and l in ent['labels']:
                        rec[f'label-{l}'] = ent['labels'][l]['value']

                    if "descriptions" in ent and l in ent['descriptions']:
                        rec[f'description-{l}'] = ent['descriptions'][l]['value']

                    if gloss and "glosses" in ent and l in ent['glosses']:
                        rec[f'gloss-{l}'] = ent['glosses'][l]['value']

                # x[queryRes].keys()
                dt.append(rec)
            return {"success": 1, "head": hdr, "data": dt}
        except Exception as e:
            return {"success": 0, "data": data}
