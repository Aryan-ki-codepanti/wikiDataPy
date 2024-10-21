

import requests
import os
from dotenv import load_dotenv
from writer import WikiWriter
import json
import csv

from time import sleep
load_dotenv()


class BulkWriter(WikiWriter):

    DELTA = 5

    def addClaimsFromCSV(self, fileSource: str, header=True):
        """
        Create a new claim on a Wikidata entity.

        :param fileSource: str, the path  of the CSV file having data as entity_id, property_id,value_id
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

    def createEntitiesFromCSV(self, fileSource: str, header=True):
        """
        Create a new  Wikidata entity per row in CSV file

        :param fileSource: str, the path  of the CSV file having

        CSV file format of rows with optional header but specify if header present
        language_code,label,description

        this creates one entity per row with a single label description at time
        for multiple labels/descriptions in more than one language , create 1 entity then use 'editEntitiesFromCSV' 
        from its ids

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
                    resp.append(self.createOrEditEntity(
                        {i[0]: i[1]}, {i[0]: i[2]}))
                    sleep(BulkWriter.DELTA)
                return resp

        except Exception as e:
            print("Error", e)
            return e
        finally:
            print(
                "If facing limit issues try after few time or increase BulkWriter.DELTA")


def bulk_add_claim_test(w: BulkWriter):
    f1 = "bulk/test1.csv"
    f2 = "bulk/test_bulkAddClaim.json"
    res = w.addClaimsFromCSV(f1)
    print("Bulk done")
    w.dumpResult(res, f2)


def bulk_create_entities(w: BulkWriter):
    f1 = "bulk/test_create.csv"
    f2 = "bulk/test_create_3.json"  # lot of creations

    res = w.createEntitiesFromCSV(f1)
    print("Bulk Create done")
    w.dumpResult(res, f2)


if __name__ == "__main__":

    # bulk add claim test

    w = BulkWriter(os.getenv("WIKI_USERNAME"), os.getenv("WIKI_PASSWORD"))
    w.login()
    w.getCSRFTtoken()

    # bulk_add_claim_test(w)

    bulk_create_entities(w)

    w.logout()
