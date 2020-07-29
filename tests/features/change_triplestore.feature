Feature: Change the underlying triplestore
  As a developer,
  I want to be able to change the underlying triplestore to be synchronized
  So operations can be executed on multiple triplestore.

    Scenario: Use of new triplestore
        Given the creation of a new triplestore adapter
        When the triplestore is selected as the one to be synchronized
        Then the synchronization operations are executed on the new triplestore
