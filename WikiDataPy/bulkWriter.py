

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

    def addClaimsFromCSV(self, fileSource: str, header: bool = True):
        """
        Create a new claim on a Wikidata entity.

        :param fileSource: str, the path  of the CSV file having data as entity_id, property_id,value_id
        :param header:  boolean specifying if csv file has header or not
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

    def createEntitiesFromCSV(self, fileSource: str, header=True, delimiter=","):
        """
        Create a new  Wikidata entity per row in CSV file

        :param fileSource: str, the path  of the CSV file having
        :param header:  boolean specifying if csv file has header or not


        CSV file format of rows (with optional header but specify if header present)
        language_code_1,label_1,description_1,alias1,language_code2,label_2,description2,alias2,... so on for desired languages


        where alias1 is pipe joined aliases

        this creates one entity per row with a  labels descriptions specified
        for multiple labels/descriptions in more than one language , create 1 entity then use 'editEntitiesFromCSV' 
        from entities' ids
        """

        if not self.csrf_token:
            print("You have no CSRF token, kindly login and then call getCSRFToken()")
            return

        try:
            with open(fileSource, "r") as f:
                reader = csv.reader(f, delimiter=delimiter)

                if header:  # header set
                    next(reader)

                resp = []
                for i in reader:

                    # create labels descriptions using triplets
                    lbl = {}
                    desc = {}
                    aliases = {}
                    for j in range(3, len(i), 4):
                        lbl[i[j-3]] = i[j-2]
                        desc[i[j-3]] = i[j-1]
                        if i[j]:
                            aliases[i[j-3]] = i[j].split('|')

                    if not aliases:
                        aliases = None
                    resp.append(self.createOrEditEntity(lbl, desc, aliases))

                    sleep(BulkWriter.DELTA)
                return resp

        except Exception as e:
            print("Error", e)
            return e
        finally:
            print(
                "If facing limit issues try after few time or increase BulkWriter.DELTA")

    def editEntitiesFromCSV(self, fileSource: str, header=True):
        """
        TODO
        Performs a edit on Wikidata entity per row in CSV file specified by entity_id

        :param fileSource: str, the path  of the CSV file having
        :param header:  boolean specifying if csv file has header or not


        CSV file format of rows (with optional header but specify if header present) 
        (can have multiple rows of same entity_id specifying different language label, description)
        entity_id,language_code,label,description

        for multiple labels/descriptions in more than one language , create 1 entity then use 'editEntitiesFromCSV' 
        from entities' ids with multiple rows , each row different language

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
                        {i[1]: i[2]}, {i[1]: i[3]}, i[0]))

                    # sleep(BulkWriter.DELTA)
                return resp

        except Exception as e:
            print("Error", e)
            return e
        finally:
            print(
                "If facing limit issues try after few time or increase BulkWriter.DELTA")


def bulk_add_claim_test(w: BulkWriter):
    f1 = "bulk/test1_CLAIM.csv"
    f2 = "bulk/test_bulkAddClaim2.json"
    res = w.addClaimsFromCSV(f1)
    print("Bulk done")
    w.dumpResult(res, f2)


def bulk_create_entities(w: BulkWriter):
    # f1 = "bulk/test_create.csv"
    # f2 = "bulk/test_create_3.json"  # lot of creations
    f1 = "bulk/testMul_create.csv"
    f2 = "bulk/test_create_5Mul.json"  # lot of creations

    res = w.createEntitiesFromCSV(f1)
    print("Bulk Create done")
    w.dumpResult(res, f2)


def bulk_edit_entities(w: BulkWriter):
    f1 = "bulk/test3_edit.csv"
    f2 = "bulk/test_edit_1.json"

    res = w.editEntitiesFromCSV(f1)
    print("Bulk Edit done")
    w.dumpResult(res, f2)


if __name__ == "__main__":

    # bulk add claim test

    w = BulkWriter(os.getenv("WIKI_USERNAME"), os.getenv("WIKI_PASSWORD"))
    w.login()
    w.getCSRFTtoken()

    # bulk_add_claim_test(w)

    bulk_create_entities(w)

    # bulk_edit_entities(w)

    w.logout()
