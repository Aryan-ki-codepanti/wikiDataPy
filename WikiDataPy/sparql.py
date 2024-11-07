import requests
from BASE import WikiBase
from reader import WikiReader
from datetime import datetime
import os
import sys
import time
import pprint
import re


class WikiSparql(WikiBase):

    API_ENDPOINT = "https://query.wikidata.org/sparql"

    # helper
    @staticmethod
    def parseResultToIds(res: dict):
        if "results" not in res:
            return ""

        if "bindings" not in res["results"]:
            return ""
        res = res["results"]["bindings"]

        ids = []
        for obj in res:
            for k in obj:
                if "value" not in obj[k]:
                    continue
                x = obj[k]["value"]
                id_ = re.findall(r"(?<=/)[^/]+", x)
                if id_:
                    id_ = id_[-1]
                    ids.append(id_)

        batch = 30
        if ids:
            batched_result = [ids[i:i + batch]
                              for i in range(0, len(ids), batch)]
            return batched_result
        return []

    # functionalities

    @staticmethod
    def execute(query: str):
        """
        Executes and return response of SPARQL query

        :param query: str, SPARQL Query to be executed
        """

        headers = {
            'User-Agent': 'Python/SPARQL',
            'Accept': 'application/sparql-results+json'
        }

        sys.stdout.flush()
        response = requests.get(WikiSparql.API_ENDPOINT, headers=headers,
                                params={'query': query})
        sys.stdout.flush()

        if response.status_code == 200:
            res = response.json()
            batch_IDS = WikiSparql.parseResultToIds(res)

            if not batch_IDS:
                return res

            complete_data = {}
            for batch in batch_IDS:
                sys.stdout.flush()
                x = WikiReader.getEntitiesByIds(
                    batch, options={"props": ["descriptions", "labels"]}, isTest=False)
                complete_data.update(x)
                sys.stdout.flush()
            return complete_data

        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None

    @staticmethod
    def execute_many(fileSource: str, delimiter: str = "---", output_format: str = "json", output: str = "single", output_dir: str = "sparql_test", lang: list[str] = ["en"]):
        """
        Executes and return responses of SPARQL queries and saves them to file(s) 

        response files will have format 'SparQL_Result_<time_stamp>.json'

        :param fileSource: str, Path to txt file containing sparql queries to be executed
        :param delimiter: str, delimiter used to separate queries in text file by default its '---'
        :param output_format: str, either 'json' or 'csv'\ndefault its json
        :param output: str, either 'single' or 'many' denoting output of queries should be in single json file or multiple json files \ndefault its single
            Note csv format will have one file per query
        :param output_dir: str,  directory name to save response files to
        """

        # fallback
        if output_format not in ["json", 'csv']:
            output_format = "json"

        # invalid output set to single
        if output not in ["single", "many"]:
            output = "single"

        elif output == "single" and output_format == "csv":
            output = "many"

        try:

            content = ""
            with open(fileSource) as f:
                content = f.read()
            queries = content.split(delimiter)

            cnt = 1
            result = []
            for query in queries:
                sys.stdout.flush()
                x = WikiSparql.execute(query)
                result.append(x)
                print(f"Executed query {cnt}")
                cnt += 1
                # time.sleep(1)
                sys.stdout.flush()

            t = datetime.now()

            # create directory if not exist
            if not os.path.isdir(output_dir):
                os.mkdir(output_dir)

            if output_format == "csv":
                for i, qRes in enumerate(result):
                    csvF = WikiSparql.convertToCSVForm(qRes, lang, gloss=True)
                    sys.stdout.flush()
                    if not csvF["success"]:
                        # write to json
                        WikiSparql.dumpResult(
                            x, f"{output_dir}/SparQL_Result_{t}_{i+1}.json")
                    else:
                        WikiSparql.dumpCSV(
                            f"{output_dir}/SparQL_Result_{t}_{i+1}.csv", csvF["head"], csvF["data"])
                    sys.stdout.flush()

            # JSON form
            else:
                if output == 'single':
                    WikiSparql.dumpResult(
                        result, f"{output_dir}/SparQL_Result_{t}.json")
                    print(f"Done Execution, stored results at {
                        output_dir}/SparQL_Result_{t}.json")
                    return result

                # one file per query
                for i, x in enumerate(result):
                    sys.stdout.flush()
                    WikiSparql.dumpResult(
                        x, f"{output_dir}/SparQL_Result_{t}_{i+1}.json")
                    sys.stdout.flush()

            print(f"Done execution check {output_dir}")
            return result

        except Exception as e:
            print("Error while executing many")
            return e


# all cats
sparql_query = """
SELECT ?item ?itemLabel
WHERE 
{
?item wdt:P31 wd:Q146.  # Find entities that are instances of "cat" (Q146)
SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 10
"""

# humans
humans = """
SELECT ?human WHERE {
?human wdt:P31 wd:Q5.  # P31: instance of, Q5: human
}
LIMIT 10

"""


def test_execute(fname):

    res = WikiSparql.execute(humans)
    # WikiSparql.parseResultToIds(res)
    print("Execute DONE")
    WikiSparql.dumpResult(res, fname)


def test_execute_many():

    res = WikiSparql.execute_many(
        "demo/7_bulkSparql.txt", output="single", output_dir="demo", output_format="json", lang=["en", "hi"])
    # res = WikiSparql.execute_many(
    #     "sparql_test/queries.txt", output="single", output_dir="bulk_sparql")
    # "sparql_test/queries.txt",  output_dir="bulk_sparql")
    # "sparql_test/queries.txt")
    print("Execute Many DONE")


if __name__ == "__main__":

    print(datetime.now())
    # test execute
    # test_execute("sparql_test/test3_IDS.json")

    # test execute many
    test_execute_many()
