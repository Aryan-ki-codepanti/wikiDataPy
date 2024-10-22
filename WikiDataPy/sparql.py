import requests
from BASE import WikiBase


class WikiSparql(WikiBase):

    API_ENDPOINT = "https://query.wikidata.org/sparql"

    @staticmethod
    def execute(query):

        # Define the query headers
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


def test_execute(fname):

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

    res = WikiSparql.execute(humans)
    print("Execute DONE")
    WikiSparql.dumpResult(res, fname)


if __name__ == "__main__":

    # test execute
    test_execute("sparql_test/test2_humans.json")

# Execute the query
# results = query_wikidata_sparql(sparql_query)

# Display the results
# if results:
#     for result in results['results']['bindings']:
#         item = result['item']['value']
#         label = result['itemLabel']['value']
#         print(f"Item: {item}, Label: {label}")
