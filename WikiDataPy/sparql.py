import requests
from BASE import WikiBase
from datetime import datetime
import os
import sys


class WikiSparql(WikiBase):

    API_ENDPOINT = "https://query.wikidata.org/sparql"

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

        response = requests.get(WikiSparql.API_ENDPOINT, headers=headers,
                                params={'query': query})

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None

    @staticmethod
    def execute_many(fileSource: str, delimiter="---", output="single", output_dir="sparql_test"):
        """
        Executes and return responses of SPARQL queries and saves them to file(s) 

        response files will have format 'SparQL_Result_<time_stamp>.json'

        :param fileSource: str, Path to txt file containing sparql queries to be executed
        :param delimiter: str, delimiter used to separate queries in text file by default its '---'
        :param output: str, either 'single' or 'many' denoting output of queries should be in single file or multiple files \ndefault its single
        :param output_dir: str,  directory name to save response files to
        """

        try:

            # invalid output set to single

            if output not in ["single", "many"]:
                output = "single"

            content = ""
            with open(fileSource) as f:
                content = f.read()
            queries = content.split(delimiter)

            cnt = 1
            result = []
            for query in queries:
                x = WikiSparql.execute(query)
                result.append(x)
                print(f"Executed query {cnt}")
                cnt += 1

            # create directory if not exist
            if not os.path.isdir(output_dir):
                os.mkdir(output_dir)

            t = datetime.now()
            if output == 'single':
                WikiSparql.dumpResult(
                    result, f"{output_dir}/SparQL_Result_{t}.json")
                print(f"Done Execution, stored results at {
                      output_dir}/SparQL_Result_{t}.json")
                return result

            # one file per query
            for i, x in enumerate(result):
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
    print("Execute DONE")
    WikiSparql.dumpResult(res, fname)


def test_execute_many():

    res = WikiSparql.execute_many(
        "sparql_test/queries.txt", output="many", output_dir="bulk_sparql")
    # "sparql_test/queries.txt",  output_dir="bulk_sparql")
    # "sparql_test/queries.txt")
    print("Execute Many DONE")


if __name__ == "__main__":

    print(datetime.now())
    # test execute
    # test_execute("sparql_test/test2_humans.json")

    # test execute many
    test_execute_many()
