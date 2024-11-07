
import requests
import pprint
from BASE import WikiBase
# from sparql import WikiSparql


class WikiReader(WikiBase):

    API_ENDPOINT = "https://test.wikidata.org/w/api.php"
    API_ENDPOINT_PROD = "https://www.wikidata.org/w/api.php"

    # helper
    def getClaimValue(vtype: str, c: dict):
        if vtype == "monolingualtext":
            return c["value"]["text"]

        elif vtype == "quantity":
            return c["value"]["amount"]

        elif vtype == "time":
            return c["value"]["time"]

        elif vtype == "wikibase-entityid":
            return c["value"]["id"]

        elif vtype == "string":
            return c["value"]
        return ""

    # functionalities

    @staticmethod
    def searchEntities(query, fields: list[str] = ["id", "description"], n: int = None, lang: str = "en", reslang: str = "en", outputFile: str = "1_searchResults.csv"):
        """
        given a query searches knowledgebase for the relevant items

        return description as 1st field along with other fields specified by fields argument

        :param fields: list of fields fields to return (id,title,url, label,description) (default id,description)
        :param lang: can be provided to perform search by but if results are empty English (en) is used as fallback
        :param reslang: get results in this language but if results are empty English (en) is used as fallback
        :param n: specifies number of descriptors to be returned, by default all will be returned

        :param outputFile: specifies number of descriptors to be returned, by default all will be returned


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

        # try to output

        if type(outputFile) != str:
            return ans

        isCSV = outputFile.endswith(".csv")
        isJSON = outputFile.endswith(".json")
        if not isCSV and not isJSON:
            print("Invalid output file")
            return ans

        if ans:
            fields = list(ans[0].keys())
            if isCSV:
                WikiBase.dumpCSV(outputFile, fields, ans)
            if isJSON:
                WikiBase.dumpResult(ans, outputFile)

        return ans

    @staticmethod
    def getEntitiesByIds(id_: list[str] = ["Q42"], options: dict = {"languages": ["en"], "sitelinks": ["enwiki"], "props": ["descriptions"]}, outputFile: str = None, isTest: bool = True):
        '''
        getEntities

        :param id_: list of ids of entities to fetch
        :param options: set options like languages sitelinks and properties to fetch
        :param outputFile: specifies number of descriptors to be returned, by default all will be returned

        default options\n
            - languages : "en"
            - props : "descriptions"
            - sites : "enwiki"

        '''
        api = WikiReader.API_ENDPOINT
        if not isTest:
            api = WikiReader.API_ENDPOINT_PROD

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

        res = requests.get(api,
                           params=options).json()

        # error handling
        if "error" in res:
            print("Error in getEntitiesByIDs")
            return res['error']
        if "entities" in res:
            res = res["entities"]

        if outputFile:
            if outputFile.endswith(".csv"):
                x = WikiReader.convertToCSVForm(
                    res, options["languages"].split("|"))
                if not x["success"]:
                    print("Can't write to csv")
                else:
                    WikiBase.dumpCSV(outputFile, x["head"], x["data"])
            elif outputFile.endswith(".json"):
                WikiBase.dumpResult(res, outputFile)
            else:
                print("Invalid output file format")

        return res

    @staticmethod
    def getClaims(id_: str = "Q42", options: dict = {"rank": "normal"}, outputFile: str = ""):
        """
        get claims of entity with ID id_

        :param id_: id of item whose claims need to be fetched
        :param outputFile: specifies number of descriptors to be returned, by default all will be returned


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

            if type(outputFile) != str:
                return res

            isCSV = outputFile.endswith(".csv")
            isJSON = outputFile.endswith(".json")

            if not isCSV and not isJSON:
                print("Invalid output file")
                return res

            if isJSON:
                WikiBase.dumpResult(res, outputFile)

            if isCSV:
                fields = list(['id', 'property_id', 'type', 'value'])
                dt = []

                for k, v in res.items():
                    for c in v:
                        if "mainsnak" in c:
                            vType = c["mainsnak"]["datavalue"]["type"]
                            rec = {
                                "id": c["id"], "property_id": k, "type": vType
                            }
                            rec["value"] = WikiReader.getClaimValue(
                                vType, c["mainsnak"]["datavalue"])
                            dt.append(rec)
                WikiBase.dumpCSV(outputFile, fields, dt)

        return res


def searchEntityTest():
    q = "ironman"
    ans = WikiReader.searchEntities(
        q, ["id", "url", "label", "description"],  reslang="hi", n=20, outputFile="demo/1_searchEntities.csv")

    ans2 = WikiReader.searchEntities(
        "हिन्दी विकिपीडिया", lang="hi", n=10, reslang="hi", outputFile="demo/1_searchEntities.json", fields=["id", "label", "description"])

    print("DONE search Entities")


def getEntitiesTest():

    # options = {"languages": ["en", "fr", "hi"], "sitelinks": [
    #     "enwiki"], "props": ["descriptions", "labels"]}
    options = {"languages": ["en", "hi"], "props": ["descriptions", "labels"]}

    ids = ["Q42", "Q298547", "Q5", "Q236478", "Q236479"]
    jackson = "Q2381"
    res = WikiReader.getEntitiesByIds(
        ids, options, outputFile="demo/2_getEntities.json")
    print("Done get entities")


def getClaimTest():
    id_ = "Q298547"
    res = WikiReader.getClaims(id_, outputFile="demo/3_getClaim.csv")
    print("Done claim test")


if __name__ == "__main__":
    r = WikiReader()
    q = "pen"

    # ans = r.searchEntities(q, ["description", "url"], n=2, lang="fr-ca")

    # search query test
    searchEntityTest()

    # get entities test
    # getEntitiesTest()

    # get claims test
    # getClaimTest()
