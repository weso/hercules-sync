Feature: Synchronize RDF changes with a Wikibase
  As an ontology engineer,
  I want ontology file changes to be synchronized with a Wikibase,
  So it can serve as a publication service for domain experts.

    Scenario: Addition of new triples
        Given an RDF file
        When a new triple is added to the file
        Then the triple will be added to the Wikibase

    Scenario: Removal of existing triples
        Given an RDF file
        When an existing triple is removed from the file
        Then the corresponding triple will be removed from the Wikibase
    
    Scenario: Modification of triples
        Given an RDF file
        When the contents of a triple are modified
        Then the modifications will be synchronized with the Wikibase
