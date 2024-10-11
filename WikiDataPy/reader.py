import requests
import pprint


class WikiReader:

    API_ENDPOINT = "https://www.wikidata.org/w/api.php"

    @staticmethod
    def searchEntities(query, fields=["description"], n=None, lang="en"):
        '''
            given a query searches knowledgebase for the items related to it
            return description as 1st fielf along with other fields specified by fields argument

            lang can be provided but if results are empty English (en) is used as fallback

            n specifies number of descriptors to be returned, by default all will be returned
        '''

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
            l = []
            for k in fields:
                if k in i:
                    l.append(i[k])
            ans.append(l)

        # unlist if only 1 field

        if not ans:
            return WikiReader.searchEntities(query, fields, n=n, lang="en")

        if n is not None:
            ans = ans[:min(n, len(ans))]

        return ans


if __name__ == "__main__":
    r = WikiReader()
    q = "pen"

    ans = r.searchEntities(q, ["description", "url"], n=2, lang="fr-ca")
    pprint.pprint(ans)
