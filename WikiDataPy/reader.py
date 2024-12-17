
import requests
import pprint
from .BASE import WikiBase
from tabulate import tabulate
from pprint import pprint


class WikiReader(WikiBase):

    API_ENDPOINT = "https://test.wikidata.org/w/api.php"
    API_ENDPOINT_PROD = "https://www.wikidata.org/w/api.php"

    # helper
    @staticmethod
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
    def searchEntities(query, fields: list[str] = ["id", "description"], n: int = None, lang: str = "en", reslang: str = "en", outputFile: str = "1_searchResults.csv", propertyFind=False, isTest=False):
        """
        given a query searches knowledgebase for the relevant items (by description , labels, aliases)

        return  field values specified by fields argument

        :param fields: list of fields fields to return (id,title,url, label,description) (default id,description)
        :param lang: can be provided to perform search by but if results are empty English (en) is used as fallback
        :param reslang: get results in this language but if results are empty English (en) is used as fallback
        :param n: specifies number of results to be returned, by default all will be returned

        :param outputFile: store output at this file (CSV/JSON)
        :param propertyFind: when set to true will search for properties (PIDs) instead of entities (QIDs)(default False)
        :param isTest: flag when set will use test.wikidata.org (for testing) instead of main site (www.wikidata.org)
        """

        api = WikiReader.API_ENDPOINT_PROD
        if isTest:
            api = WikiReader.API_ENDPOINT

        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": lang,
            "search": query,
            "uselang": reslang
        }

        if propertyFind:
            params["type"] = "property"

        if n:
            params["limit"] = n

        res = requests.get(api, params=params).json()
        res = [] if "search" not in res else res["search"]
        # pprint(res)

        ans = []
        for i in res:
            l = {}
            for k in fields:
                if k in i:
                    l[k] = i[k]
            ans.append(l)

        # fallback to english language if no result
        if not ans:
            return WikiReader.searchEntities(query, fields, n=n, lang=lang, reslang=reslang, outputFile=outputFile, propertyFind=propertyFind, isTest=isTest)

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
    def getEntitiesByIds(id_: list[str] = ["Q42"], options: dict = {"languages": ["en"], "sitelinks": ["enwiki"], "props": ["descriptions"]}, outputFile: str = None, isTest: bool = False):
        """
        Fetch get entities from ids 

        :param id_: list of ids of entities to fetch
        :param options: set options like languages sitelinks and properties to fetch
        :param outputFile: specifies number of descriptors to be returned, by default all will be returned
        :param isTest: flag when set will use test.wikidata.org (for testing) instead of main site (www.wikidata.org)

        default options\n
            - languages : "en"
            - props : "descriptions"
            - sites : "enwiki"

        """

        api = WikiReader.API_ENDPOINT_PROD
        if isTest:
            api = WikiReader.API_ENDPOINT

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
    def getClaims(id_: str = "Q42", options: dict = {"rank": "normal"}, outputFile: str = "", isTest: bool = False):
        """
        get claims of entity with ID id_

        :param id_: id of item whose claims need to be fetched
        :param outputFile: specifies output file (JSON/CSV)
        :param isTest: flag when set will use test.wikidata.org (for testing) instead of main site (www.wikidata.org)


        :param options:
            - rank: normal default (One of the following values: deprecated, normal, preferred)
        """

        api = WikiReader.API_ENDPOINT_PROD
        if isTest:
            api = WikiReader.API_ENDPOINT

        options.update(
            {"format": "json", "action": "wbgetclaims", "entity": id_})

        res = requests.get(api,
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

    @staticmethod
    def getRelatedEntitiesProps(id_: str,  limit=None, isTest=False):
        """
        this method gets (PID,Q2_ID) pairs for entity
        i.e. properties and value ids for an entity

        :param id_: QID of entity
        :param limit: when set , will return no more than limit no. of pairs
        :param isTest: flag when set will use test.wikidata.org (for testing) instead of main site (www.wikidata.org)
        """
        claims = WikiReader.getClaims(id_, outputFile=None, isTest=isTest)
        ans = set()
        for k, v in claims.items():
            if v[0]["mainsnak"]["datavalue"]["type"] == "wikibase-entityid":
                ans.add((k, v[0]["mainsnak"]["datavalue"]["value"]["id"]))

            if limit and limit == len(ans):
                return list(ans)

        return list(ans)

    @staticmethod
    def reverseLookup(label, lang='en', limit=None, propertyFind=False, isTest=False):
        """
        Lookup entities by label 
        :param label: label/ query to lookup entities by
        :param limit: if set returns no more than limit no. of results
        :param lang:  language to search by (default 'en')


        :param propertyFind: when set to true will search for properties (PIDs) instead of entities (QIDs)(default False)
        :param isTest: flag when set will use test.wikidata.org (for testing) instead of main site (www.wikidata.org)

        """
        x = WikiReader.searchEntities(
            label, ['id', 'label', 'aliases', 'description'], lang=lang, outputFile=None, propertyFind=propertyFind, isTest=isTest)
        if limit:
            return x[:limit]
        return x

    @staticmethod
    def getEntitiesRelatedToGiven(name: str, lang='en', propertyFind=False, isTest: bool = False):
        """
        tries to fetch entities similar to the one specified by name

        :param name: name to find entity by
        :param lang:  language to search by (default 'en')
        :param propertyFind: when set to true will search for properties (PIDs) instead of entities (QIDs)(default False)
        :param isTest: flag when set will use test.wikidata.org (for testing) instead of main site (www.wikidata.org)
        """
        e1 = WikiReader.reverseLookup(
            name, lang=lang, propertyFind=propertyFind, isTest=isTest)

        if not e1:
            return
        i = j = 1
        data = {}

        keys = e1[0].keys()

        for key in keys:
            mp = []
            for x in e1:
                if key == "aliases":
                    if "aliases" in x:
                        mp.append(", ".join(x["aliases"]))
                    else:
                        mp.append("")
                else:
                    mp.append(x.get(key, ""))

            data[key] = mp

        print(tabulate(data, headers="keys", tablefmt="grid", showindex=True))
        idx = eval(input(f"Enter index of item you want meant by\n'{
                   name}'\n(Default would be 0) "))
        if not idx or type(idx) != int or idx < 0 or idx >= len(e1):
            idx = 0
        return e1[idx]


def searchEntityTest():
    q = "ironman"
    ans = WikiReader.searchEntities(
        q, ["id", "url", "label", "description"],  reslang="hi", n=20, outputFile="demo/1_searchEntities.csv")

    ans2 = WikiReader.searchEntities(
        "हिन्दी विकिपीडिया", lang="hi", n=10, reslang="hi", outputFile="demo/1_searchEntities.json", fields=["id", "label", "description"])


def getEntitiesTest():

    # options = {"languages": ["en", "fr", "hi"], "sitelinks": [
    #     "enwiki"], "props": ["descriptions", "labels"]}
    options = {"languages": ["en", "hi"], "props": ["descriptions", "labels"]}

    ids = ["Q42", "Q236478", "Q236479"]
    res = WikiReader.getEntitiesByIds(
        ids, options, outputFile="demo/2_getEntities_2.csv")
    print("Done get entities")


def getClaimTest():
    id_ = "Q42"
    id_ = "Q236479"
    res = WikiReader.getClaims(
        id_, outputFile="demo/3_getClaim_2.csv")
    print("Done claim test")


def reverseLookupTest():
    lbl = 'chocolate'
    res = WikiReader.reverseLookup(lbl)
    pprint(res)
    # WikiReader.dumpResult(res, "chocolate.json")


def test_get_related():
    q = input("Query : ")
    res = WikiReader.getEntitiesRelatedToGiven(q, propertyFind=True)
    pprint(res)


if __name__ == "__main__":
    pass
    # search query test
    # searchEntityTest()

    # get entities test
    # getEntitiesTest()

    # get claims test
    # getClaimTest()

    # reverseLookup test
    # reverseLookupTest()

    # test  get related
    # test_get_related()
