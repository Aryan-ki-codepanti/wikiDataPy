# WikidataPy

WikidataPy is a Python library designed for seamless interaction with Wikidata's API, enabling users to perform a variety of operations such as searching entities, retrieving claims, performing SPARQL queries, and even visualizing knowledge graphs.

---

## Features

-   **Entity Search and Retrieval**: Search for entities using labels, descriptions, or aliases.
-   **Read and Write Operations**:
    -   Retrieve claims and other entity details.
    -   Add or edit claims and entities.
    -   Perform bulk operations using CSV files.
-   **SPARQL Query Execution**: Execute custom SPARQL queries for advanced data retrieval.
-   **Knowledge Graph Visualization**: Visualize the relationships between entities and their properties.
-   **Test Environment Support**: Perform operations on `test.wikidata.org` to avoid affecting production data.

---

## Installation

```bash
pip install WikiDataPy
```

---

## Usage

for Usage refer to usage scripts in github repository  
each method has docstring writter for ease of understanding parameters, accepted CSV format and other things

There are 4 modules and classes in which functionality is divided and some methods provided are

1.  **`WikiReader`**: searchEntities , getEntitiesByIds , getClaims , getEntitiesRelatedToGiven

2.  **`WikiWriter`**: (Requires wikidata account's username, password )

    -   `methods`: login , getCSRFtoken , logout, addClaim, removeClaims, createOrEditEntity, delete_entity(admins,moderators), setLabel, setDescription, setAliases, addRemoveAliases

        `usage`

        -   create object : w = WikiWriter(`your_username`,`your_password`)
        -   login : w.login()
        -   get token: w.getCSRFtoken()
        -   perform operations : w.getClaims(), w.createOrEditEntity() etc
        -   logout : w.logout()

3.  **`BulkWriter`**: (Requires wikidata account's username, password )

    -   `methods` and accepted CSV format with / without header:

        -   `addClaimsFromCSV` : _<entity_id, property_id, value_id>_
        -   `addClaimsFromNamesCSV` : _<entity_name, property_id, value_name>_
        -   `createEntitiesFromCSV` : _<language_code_1,label_1,description_1,alias1,language_code2,label_2,description2,alias2,...>_
        -   `editEntitiesFromCSV` : _<entity_id,language_code,label,description,aliases>_

        `usage`

        -   create object : w = BulkWriter(`your_username`,`your_password`)
        -   login : w.login()
        -   get token: w.getCSRFtoken()
        -   perform operations : w.addClaimsFromNamesCSV(), w.createEntitiesFromCSV() etc
        -   logout : w.logout()

4.  **`WikiGraph`**: buildGraph , plotGraph (with IDs), plotNamedGraph (with names )

    -   `usage`
        -   create object : w = WikiGraph("Q42") or WikiGraph("Ronaldo")
        -   call w.buildGraph(radius,out_degree) : default are (3,3)
        -   call w.plotGraph() or w.plotNamedGraph() with save file name optionally

5.  **`WikiSparql`**: Execute custom SPARQL queries for advanced data retrieval.
    -   `methods`
        -   execute(query) : execute single query
        -   execute_many(source_text,...) : execute many queries from a text file that are delimited (default "---")
        -   find_entities_by_property(pname,ename) : Fetches entities based on a specified property and entity type.

---

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests for new features or bug fixes.

---
