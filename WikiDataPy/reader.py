
import requests
import pprint
from BASE import WikiBase


class WikiReader(WikiBase):

    @staticmethod
    def searchEntities(query, fields=["id", "description"], n=None, lang="en", reslang="en"):
        """
        given a query searches knowledgebase for the relevant items

        return description as 1st field along with other fields specified by fields argument

        :param fields: list of fields fields to return (id,title,url, label,description) (default id,description)
        :param lang: can be provided to perform search by but if results are empty English (en) is used as fallback
        :param reslang: get results in this language but if results are empty English (en) is used as fallback
        :param n: specifies number of descriptors to be returned, by default all will be returned
        """

        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": lang,
            "search": query,
            "uselang": reslang
        }

        if n:
            params["limit"] = n
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

        # fallback to english language if no result
        if not ans:
            return WikiReader.searchEntities(query, fields, n=n)

        return ans

    @staticmethod
    def getEntitiesByIds(id_=["Q42"], options={"languages": ["en"], "sitelinks": ["enwiki"], "props": ["descriptions"]}):
        '''
        getEntities

        :param id_: list of ids of entities to fetch
        :param options: set options like languages sitelinks and properties to fetch

        default options\n
            - languages : "en"
            - props : "descriptions"
            - sites : "enwiki"


        '''

        id_ = "|".join(id_)
        if "sitelinks" in options:
            options["sitelinks"] = "|".join(options["sitelinks"])
        if "languages" in options:
            options["languages"] = "|".join(options["languages"])
        if "props" in options:
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
    q = "ironman"
    ans = WikiReader.searchEntities(
        q, ["description", "url", "id"],  lang="hi", n=20)

    ans2 = WikiReader.searchEntities(
        "हिन्दी विकिपीडिया", lang="hi", n=10, reslang="en")
    # pprint.pprint(ans2)
    print("DONE search Entities")
    WikiReader.dumpResult(ans2, fname)


def getEntitiesTest(fname):

    # options = {"languages": ["en", "fr", "hi"], "sitelinks": [
    #     "enwiki"], "props": ["descriptions", "labels"]}
    options = {"props": ["descriptions", "labels"]}

    ids = ["Q42", "Q298547", "Q5"]
    jackson = "Q2381"
    res = WikiReader.getEntitiesByIds(ids, options)
    print("Done get entities")
    WikiReader.dumpResult(res, fname)


def getClaimTest(fname):
    id_ = "Q298547"
    res = WikiReader.getClaims(id_)
    print("Done claim test")
    WikiReader.dumpResult(res, fname)


if __name__ == "__main__":
    r = WikiReader()
    q = "pen"

    # ans = r.searchEntities(q, ["description", "url"], n=2, lang="fr-ca")

    # search query test
    searchEntityTest("demo/1_searchEntities.json")

    # get entities test
    # getEntitiesTest("reader_result/test_GetEntities3.json")

    # get claims test
    # getClaimTest("reader_result/test_GetClaimTest3.json")
