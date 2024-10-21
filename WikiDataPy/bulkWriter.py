

import requests
import os
from dotenv import load_dotenv
from writer import WikiWriter
import json
import csv
load_dotenv()


class BulkWriter(WikiWriter):

    def addClaimsFromCSV(self, fileSource: str, header=True):
        """
        Create a new claim on a Wikidata entity.

        :param fileSource: str, the path  of the CSV file having data as entity_id, property_id,value_id
        :param fileDest: str, the path  of the JSON file to keep response
        """

        if not self.csrf_token:
            print("You have no CSRF token, kindly login and then call getCSRFToken()")
            return

        try:
            with open(fileSource, "r") as f:
                reader = csv.reader(f)

                if header:  # header set
                    next(reader)

                resp = []
                for i in reader:
                    resp.append(self.addClaim(i[0], i[1], i[2]))
                return resp
        except Exception as e:
            print("Error", e)
            return e


def bulk_add_claim_test(w: BulkWriter):
    f1 = "bulk/test1.csv"
    f2 = "bulk/test_bulkAddClaim.json"
    res = w.addClaimsFromCSV(f1)
    print("Bulk done")
    w.dumpResult(res, f2)


if __name__ == "__main__":

    # bulk add claim test

    w = BulkWriter(os.getenv("WIKI_USERNAME"), os.getenv("WIKI_PASSWORD"))
    w.login()
    w.getCSRFTtoken()

    bulk_add_claim_test(w)

    w.logout()
