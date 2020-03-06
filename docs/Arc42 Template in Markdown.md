# Hercules synchronization module documentation

**About arc42**

arc42, the Template for documentation of software and system
architecture.

By Dr. Gernot Starke, Dr. Peter Hruschka and contributors.

Template Revision: 7.0 EN (based on asciidoc), January 2017

© We acknowledge that this document uses material from the arc 42
architecture template, <http://www.arc42.de>. Created by Dr. Peter
Hruschka & Dr. Gernot Starke.

> **Note**
>
> This version of the template contains some help and explanations. It
> is used for familiarization with arc42 and the understanding of the
> concepts. For documentation of your own system you use better the
> *plain* version.

## Introduction and Goals
This document includes the architectural documentation for the synchronization module - from now on called _hercules\_sync_ - between ontology files and a triple-store, whis is a part of the ontological infrastructure of Project Hércules.

The structure of this document follows the [arc42](https://arc42.org/) template for documentation of software and systems architectures.

### Requirements Overview
The overall goal of _hercules\_sync_ is to allow

### Quality Goals
In this section we will enumerate the top quality goals for the system's architecture:

| Code | Description | Scenario |
| ---- | ----------- | -------- |
| | |

### Stakeholders

| Role/Name   | Description                   | Expectations              |
| ----------- | ------------------------- | ------------------------- |
| | Contact-1                 | *&lt;Expectation-1*&gt;   |
|      | Contact-2                 | *&lt;Expectation-2*&gt;   |

## Architecture Constraints

| Contraint | Description                            |
|:---------:|----------------------------------------|
|     C1    | The system must be developed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html). |
|     C2    | The system must be platform-independent and should run on the major operating systems (Windows™, Linux, and Mac-OS™). |
|     C3    | The system must be runnable from the command line. |
|     C4    | The control versions system used to store the ontologies will be git based.  |
|     C5    |  |

## System Scope and Context

### Business Context

### Technical Context

## Solution Strategy
* Use
*

## Building Block View
The following diagram shows the static decomposition of the system into building blocks:

![](images/herc_sync_bbview.png)

### Whitebox hercules_sync

#### Rationale
T

#### Contained Blackboxes

#### Interfaces

#### Diff Processor

#### Ontology Synchronizer

#### Triple-Store Manager

### Level 2
In this level we will detail each one of the previous building blocks of the system identified in level 1.

> __Python singularities__. <br>
> Since Python is a dynamically typed language that lacks some of the constructs of other programming languages, such as Interfaces, we will be making the following distinctions in the UML diagrams:
> * Python modules which are just composed of functions, and do not have any classes inside, will be treated as static classes in the UML diagrams.
> * Since access modifiers don't exist in Python, we used the convention that underscored fields and funtions are considered private. These items will be shown as private in the UML diagrams.
> * Since there are no interfaces in Python, we will represent as an interface abstract classes that do not have any field or implemented method.
> * Multiple inheritance is possible in Python, so there could be cases in the UML diagrams where a class extends multiple classes.
>
> Also, it’s important to note that Python relies in duck typing rather than in implementation of interfaces. However, we still opted to create ”pseudo-interfaces” (abstract classes with no fields or imple- mented methods) and extend them by other classes. This was done in order to specify explicitly that a class followed a given interface, rather than implicitly by checking at the methods that it provides internally.

#### Listener
* Listener: The listener class initializes a flask server through the AppFactory, and establishes the entrypoint where information about the ontologies' updates will be received.
* Webhook: This class manages the communication with the control version system through Webhooks (for more information about webhooks, see https://developer.github.com/webhooks/) in a safe manner with the use of RSA keys.
* AppFactory: Factory class that creates the Flask application given a specific server configuration.
* Config: Configuration class to be used by the server.

<p align="center">
  <img src="images/herc_sync_listener_classes.png" width=500>
</p>


#### Diff Processor
* PushEventHandler: Main class used by the listener to process all the received information about incoming changes from the ontologies.
* PushInfo: Information about the data received from the control version system.
* GitDiffParser: This class is in charge of parsing the diff about each file changed and return the lines that were modified in each file.
* GitDataLoader: The GitDataLoader class will download the content of each file before and after the modifications were done.
* GitFile: Wrapper which stores the content of a modified file before and after the modification, as well as other metadata about the file.

<p align="center">
  <img src="images/herc_sync_diff_parser_classes.png" width=600>
</p>

#### Ontology Synchronizer
* OntologySynchronizer: This class receives the synchronization algorithm to be used and returns a list of operations to perform on the triple-store to reflect the current modifications from the ontology files.
* SyncAlgorithm: Interface to be implemented by each one of the synchronization algorithms. These algorithms receive the modified lines from each file and return the list of operations to be made.
* NaiveSync: Simple synchronization algorithms that overwrites the content of the triple-store to be consistent with the current state of the ontology files.
* RDFSync: [RDFSync](https://link.springer.com/content/pdf/10.1007%2F978-3-540-76298-0_39.pdf) algorithm for the synchronization of RDF files.
* SyncOperation: Abstract class that represents the operation to be made in the triple-store.

<p align="center">
  <img src="images/herc_sync_ontologies_synchronizer_classes.png">
</p>

#### Triple-Store Manager
* TripleStoreManager: Interface to be implemented by each one of the adapters that will connect to a specific triple-store.
* WikibaseAdapter: Adapter that connects to a BlazeGraph triple-store configured in a wikibase instance.
* ModificationResult: Class which encapsulates the result of a modification performed on a triple-store.

<p align="center">
  <img src="images/herc_sync_triplestore_manager_classes.png" width=500>
</p>

## Runtime View

### Modify an ontology file

### Direct modification of the triple store

## Deployment View

### Infrastructure Level 1

### Infrastructure Level 2

#### *&lt;Infrastructure Element 1&gt;*


#### *&lt;Infrastructure Element 2&gt;*

#### *&lt;Infrastructure Element n&gt;*

## Technical and Cross-cutting Concepts

### Technologies used

#### Python
The main programming language used for the module implementation is [Python](https://www.python.org). Python is a interpreted, high level and general purpose language designed by Guido van Rossum in 1991. It is characterized by its legible syntax and dynamic typing.

Python was chosen for the implementation of this module since it provides a wide ecosystem of libraries that allow working with ontologies and triple stores compared to other languages.

This module will have compatibility with Python 3. Since January 1st of 2020 the end of cycle of Python 2 was announced, and Python 3 is the current maintained version.

#### Flask
[Flask](https://palletsprojects.com/p/flask/) is a web microframework based on the [WSGI](https://wsgi.readthedocs.io/en/latest/) standard which focuses on flexibility and efficiency.

Flask will be used in _hercules\_sync_ to launch a web server that will listen to ontology updates coming from the control version system.

#### WikidataIntegrator
[WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) is a library that allows the creation and querying of entity data on a wikibase instance through the [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page).

This library is used to reflect the modifications --- in the triple store.

Esta librería es utilizada para introducir las modificaciones que se hayan producido en las ontologías en la instancia de Wikibase donde se encuentra el triple-store.

#### Pytest
Pytest es un framework que facilita la implementación de pruebas con Python. Puede ser utilizado tanto para escribir pruebas sencillas, como para realizar pruebas funcionales más complejas. Las librerías de pruebas que vienen por defecto en el lenguaje, como unittest y doctest, pueden ser facilmente integradas con pytest.

#### Travis
Travis es un servicio de integración continua que puede ser usado para monitorizar y probar proyectos alojados en GitHub.

#### Codacy
Codacy es una herramienta de análisis de código estática que permite la monitorización de calidad de proyectos, con soporte para múltiples lenguajes de programación. Devuelve varias métricas de calidad, como por ejemplo la seguridad, compatibilidad, rendimiento o estilo de código.

### Continuous integration
In the module repository we follow continuous integration practices in order to fulfill some of the non-functional requirements that need to be met. Before a new version of the module is pushed to the repository, a Travis build is launched where all the tests are executed. In order to be able to upload new changed to the master branch all tests need to pass, and both code coverage and quality returned by Codecov and Codacy must not drop below a given threshold.

### Style guides
The main coding standard that was followed was the [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python style guide. This standard specifies how code written in Python should be formatted (number of characters per line, import formats...) and is widely adopted in the community.

In order to document the code there are also several formatting styles that can be used. In our case, we opted to use the [numpy docstring style](https://numpydoc.readthedocs.io/en/latest/format.html) due to the readability it provides when compared to other alternatives.

## Design Decisions

### Adapter pattern: Changing the triple-store implementation

### Strategy pattern: Creating and using multiple synchronization algorithms

## Quality Requirements

### Quality Tree

### Quality Scenarios

## Risks and Technical Debts

## Tests
### Design phase
In order to test this module the following techniques will be used:
* Static techniques:
  * Static code analysis tools.
* Dynamic techniques:
  * Specification-based, with equivalence class partitioning.

These techniques were selected mainly due to the nature of the system (there is no graphical interface, so other static techniques were more difficult to use) and also due to the experience of the development team testing related systems (experience based techniques were not appropriate for this context).

The following test levels will be automatised and documented for this system:
* Unit and component tests.
* Integration tests.

### Implementation phase
All the tests that will be implemented, as well as their respective results will be added to this section as the development of the system goes forward.

## Glossary

| Term                              | Definition                        |
| --------------------------------- | --------------------------------- |
| Term 1                            | &lt;definition-1&gt;              |
| Term 2                            | &lt;definition-2&gt;              |
