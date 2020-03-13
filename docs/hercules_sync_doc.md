# Hercules synchronization module architecture

> __Note: WORK IN PROGRESS__ <br>
> This document is being updated in a weekly basis and is currently a work in progress.


## Introduction and Goals
This document includes the architectural documentation for the synchronization module - from now on called _hercules\_sync_ - between ontology files and a triple-store, whis is a part of the ontological infrastructure of Project Hércules.

The structure of this document follows the [arc42](https://arc42.org/) template for documentation of software and systems architectures.

### Requirements Overview
The overall goal of _hercules\_sync_ is to syncrhonize ontologies content between files hosted in a version control system and a triplestore where the content is stored.

A more complete analysis of the system's requirements can be found in the __Requirements analysis__ section.

### Quality Goals
In this section we will enumerate the top quality goals for the system's architecture:

| Priority | Goal | Scenario |
| ---- | ----------- | -------- |
| 1 | Consistency | |
| 1 | Flexibility | |
| 1 | Fault Tolerance | |

### Stakeholders

| Role/Name   | Description                   | Expectations              |
| ----------- | ------------------------- | ------------------------- |
| Domain Experts | User that modifies the content of the ontology through the user interface provided by the ontology publication service. | When a change is made through the user interface, the content of the ontologies in the version control system should be consistent with these changes. |
| Ontology Engineer | User that modifies the content of the ontology directly from the version control system. | Once a ontology file is modified, the changes should be reflected in the triplestore. |

## Architecture Constraints

| Contraint | Description                            |
|:---------:|----------------------------------------|
|     C1    | The system must be developed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html). |
|     C2    | The system must be platform-independent and should run on the major operating systems (Windows™, Linux, and Mac-OS™). |
|     C3    | The system must be runnable from the command line. |
|     C4    | The control versions system used to store the ontologies will be git based.  |

## System Scope and Context

### Business Context

### Technical Context

## Solution Strategy
* Use

## Building Block View
The following diagram shows the static decomposition of the system into building blocks:

![](images/herc_sync_bbview.png)

### Whitebox hercules_sync

#### Rationale


#### Contained Blackboxes
Los componentes e interfaces detectados son los siguientes:
* listener: Este componente es el punto de entrada al subsistema por parte de otros sistemas externos. Para ello ofrece una interfaz al exterior, llamada OnWebhook, que es la encargada de recibir los datos sobre las actualizaciones de las ontologías por parte del CVS.
* ontology_synchronizer: Este componente realiza la sincronización de los cambios recibidos, creando operaciones a realizar en el triple_store para reflejar estos cambios. Ofrece una interfaz llamada _SynchronizeOntologies_, que es utilizada por el componente listener para sincronizar los cambios recibidos.
* diff_parser: El componente _diff\_parser_ se encarga de procesar la información del diff de los ficheros típica de los sistemas de control de versiones basados en Git. Ofrece una interfaz _ParseDiff_, que es utilizada por el componente _ontology\_synchronizer_ para obtener información detallada sobre los cambios en los ficheros de ontologías.
* triplestore_manager: Por último, el componente _triplestore\_manager_ se encarga de ejecutar las operaciones recibidas del componente _ontology\_synchronizer_ sobre el triple-store elegido. Para ello ofrece el interfaz _ExecuteModification_.

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

![](images/herc_sync_listener_classes.png)


#### Diff Processor
* PushEventHandler: Main class used by the listener to process all the received information about incoming changes from the ontologies.
* PushInfo: Information about the data received from the control version system.
* GitDiffParser: This class is in charge of parsing the diff about each file changed and return the lines that were modified in each file.
* GitDataLoader: The GitDataLoader class will download the content of each file before and after the modifications were done.
* GitFile: Wrapper which stores the content of a modified file before and after the modification, as well as other metadata about the file.

![](images/herc_sync_diff_parser_classes.png)

#### Ontology Synchronizer
* OntologySynchronizer: This class receives the synchronization algorithm to be used and returns a list of operations to perform on the triple-store to reflect the current modifications from the ontology files.
* SyncAlgorithm: Interface to be implemented by each one of the synchronization algorithms. These algorithms receive the modified lines from each file and return the list of operations to be made.
* NaiveSync: Simple synchronization algorithms that overwrites the content of the triple-store to be consistent with the current state of the ontology files.
* RDFSync: [RDFSync](https://link.springer.com/content/pdf/10.1007%2F978-3-540-76298-0_39.pdf) algorithm for the synchronization of RDF files.
* SyncOperation: Abstract class that represents the operation to be made in the triple-store.

![](images/herc_sync_ontologies_synchronizer_classes.png)

#### Triple-Store Manager
* TripleStoreManager: Interface to be implemented by each one of the adapters that will connect to a specific triple-store.
* WikibaseAdapter: Adapter that connects to a BlazeGraph triple-store configured in a wikibase instance.
* ModificationResult: Class which encapsulates the result of a modification performed on a triple-store.

![](images/herc_sync_triplestore_manager_classes.png)

## Runtime View

### Modify an ontology file

### Direct modification of the triple store

## Deployment View

## Technical and Cross-cutting Concepts
In this section we will

### Technologies used
The following technologies have been used in the development of the system.

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
In the module repository we follow continuous integration practices in order to fulfill some of the non-functional requirements that need to be met. Before a new version of the module is pushed to the repository, a Travis build is launched where all the tests are executed. In order to be able to upload new changes to the master branch all tests need to pass, and both code coverage and quality returned by Codecov and Codacy must not drop below a given threshold.

### Style guides
The main coding standard that was followed was the [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python style guide. This standard specifies how code written in Python should be formatted (number of characters per line, import formats...) and is widely adopted in the community.

In order to document the code there are also several formatting styles that can be used. In our case, we opted to use the [numpy docstring style](https://numpydoc.readthedocs.io/en/latest/format.html) due to the readability it provides when compared to other alternatives.

## Design Decisions

### Adapter pattern: Changing the triple-store implementation

### Strategy pattern: Creating and using multiple synchronization algorithms

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

## Requirements analysis
### Functional requirements

| Code        | Description          |
|:-----------:|:---------------------|
| FR1         | The system will establish an entry point where the information about the updates of the ontologies will be received. |
| FR2         | The system will process the information received from the Control Version System with respect to the updates in the ontologies. |
| FR3         | The system will detect the modifications to perform in the triplestore based on the information about the updates previously processed. |
| FR4         | The system will connect to a triplestore to reflect the changes from the ontologies. |
| FR5         | The system will also execute the inverse synchronization: from changes made in the triplestore to the ontology files. |
| FR6         | The system will use logging tools to detect anomalies in its internal functioning. |

### Non-functional requirements

| Code          | Description          |
|:-------------:|:---------------------|
| NFR1      | Security: The system will receive update notifications from the CVS in a safe way with the use of RSA keys. |
| NFR2      | Security: The system will use the OAuth protocol to update the triplestore. |
| NFR3 | Compatibility: The system will be at least compatible with versions 3.6, 3.7 and 3.8 of the Python programming language. |
| NFR4 | Mantenibility: The implementation of the system will follow the PEP8 standard. |
| NFR5 | Quality: Code coverage of each new released version will be at least 90%. |
| NFR6 | Extensibility: The system will facilitate the use of different triplestores where the ontologies can be stored. |

## Glossary

| Term                              | Definition                        |
|:--------------------------------- | --------------------------------- |
| OAuth | Authorization protocol that describes how unrelated servers can safely allow authorized access between them. |
| RSA | Public-key cryptosystem used for secure data transmission. |
| Triplestore | Specific type of database designed for the storage and retrieval of triples with the use of semantic queries. |
| Version Control System | Software tool that helps a software team with the management of changes to source code. |
