Feature: Modify the synchronization algorithms
  As an ontology engineer,
  I want to find information online,
  So I can learn new things and get tasks done.

    Scenario: Addition of new triples
        Given the DuckDuckGo home page is displayed
        When the user searches for "panda"
        Then results are shown for "panda"
