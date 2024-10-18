
import requests
import pprint
from BASE import WikiBase


class WikiReader(WikiBase):

    @staticmethod
    def searchEntities(query, fields=["description"], n=None, lang="en"):
        """
        given a query searches knowledgebase for the items related to it

        return description as 1st field along with other fields specified by fields argument

        :param fields: list of fields fields to return (id,title,url, label,description) (default description)
        :param lang: can be provided but if results are empty English (en) is used as fallback
        :param n: specifies number of descriptors to be returned, by default all will be returned

        """

        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": lang,
            "search": query
        }

        res = requests.get(WikiReader.API_ENDPOINT, params=params).json()
        res = [] if "search" not in res else res["search"]
        # pprint.pprint(res)

        ans = []
        for i in res:
            l = {}
            for k in fields:
                if k in i:
                    l[k] = i[k]
            ans.append(l)

        # unlist if only 1 field

        if not ans:
            return WikiReader.searchEntities(query, fields, n=n, lang="en")

        if n is not None:
            ans = ans[:min(n, len(ans))]

        return ans

    @staticmethod
    def getEntitiesByIds(id_=["Q42"], options={"languages": ["en"], "sitelinks": ["enwiki"], "props": ["descriptions"]}):
        '''
        getEntities

        :param id_: list of ids of entities to fetch
        :param options: set options like languages sitelinks and properties to fetch

        default options\n
            - languages : "en"
            - languages : "descriptions"
            - sites : "enwiki"


        '''

        id_ = "|".join(id_)
        options["sitelinks"] = "|".join(options["sitelinks"])
        options["languages"] = "|".join(options["languages"])
        options["props"] = "|".join(options["props"])

        # musrt have options
        options.update(
            {"format": "json", "action": "wbgetentities", "ids": id_})

        res = requests.get(WikiReader.API_ENDPOINT,
                           params=options).json()

        # error handling
        if "error" in res:
            print("Error in getEntitiesByIDs")
            return res['error']
        if "entities" in res:
            res = res["entities"]

        return res

    @staticmethod
    def getClaims(id_="Q42", options={"rank": "normal"}):
        """
        get claims of entity with ID id_

        :param id_: id of item whose claims need to be fetched

        options
            - rank: normal default (One of the following values: deprecated, normal, preferred)
        """

        options.update(
            {"format": "json", "action": "wbgetclaims", "entity": id_})

        res = requests.get(WikiReader.API_ENDPOINT,
                           params=options).json()

        if "error" in res:
            print("Error in get claims")
            return

        if "claims" in res:
            res = res["claims"]

        return res


def searchEntityTest(fname):
    q = "modi"
    ans = WikiReader.searchEntities(
        q, ["description", "url", "id"],  lang="en", n=10)
    print("DONE search Entities")
    WikiReader.dumpResult(ans, fname)


def getEntitiesTest(fname):

    options = {"languages": ["en", "fr"], "sitelinks": [
        "enwiki", "frwiki"], "props": ["descriptions", "labels"]}

    ids = ["Q42", "Q150", "Q123"]
    id_ = "Q150"
    jackson = "Q2381"
    res = WikiReader.getEntitiesByIds(ids, options)
    print("Done get entities")
    WikiReader.dumpResult(res, fname)


def getClaimTest(fname):
    id_ = "Q5"
    res = WikiReader.getClaims(id_)
    print("Done claim test")
    WikiReader.dumpResult(res, fname)


if __name__ == "__main__":
    r = WikiReader()
    q = "pen"

    # ans = r.searchEntities(q, ["description", "url"], n=2, lang="fr-ca")

    # search query test
    searchEntityTest("test_SearchEntity3.json")

    # get entities test
    # getEntitiesTest("test_GetEntities1.json")

    # get claims test
    # getClaimTest("test_GetClaimTest1.json")
