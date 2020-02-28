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

### Whitebox Overall System


#### &lt;Name black box 1&gt;

#### &lt;Name black box 2&gt;


#### &lt;Name black box n&gt;


#### &lt;Name interface 1&gt;


#### &lt;Name interface m&gt;

### Level 2


#### White Box *&lt;building block 1&gt;*

#### White Box *&lt;building block 2&gt;*


#### White Box *&lt;building block m&gt;*


### Level 3

#### White Box &lt;\_building block x.1\_&gt;


#### White Box &lt;\_building block x.2\_&gt;


#### White Box &lt;\_building block y.1\_&gt;


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

## Design Decisions

### Adapter pattern: Changing the triple-store implementation

### Strategy pattern: Creating and using multiple synchronization algorithms

## Quality Requirements

### Quality Tree

### Quality Scenarios

## Risks and Technical Debts

## Glossary

| Term                              | Definition                        |
| --------------------------------- | --------------------------------- |
| Term 1                            | &lt;definition-1&gt;              |
| Term 2                            | &lt;definition-2&gt;              |
