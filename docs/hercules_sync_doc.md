# Documentación del módulo hercules-sync

## Tabla de contenido
<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:0 orderedList:1 -->

1. [Introducción](#introducción)
2. [Alcance](#alcance)
3. [Requisitos](#requisitos)
	1. [Requisitos funcionales](#requisitos-funcionales)
	2. [Requisitos no funcionales](#requisitos-no-funcionales)
4. [Diseño](#diseño)
	1. [Diagrama de componentes](#diagrama-de-componentes)
	2. [Diseño de clases](#diseño-de-clases)
		1. [Componente listener](#componente-listener)
		2. [Componente diff_parser](#componente-diffparser)
		3. [Componente ontologies_synchronizer](#componente-ontologiessynchronizer)
		4. [Componente triplestore_manager](#componente-triplestoremanager)
5. [Implementación](#implementación)
	1. [Guías de estilo](#guías-de-estilo)
	2. [Tecnologías utilizadas](#tecnologías-utilizadas)
		1. [Python](#python)
		2. [Flask](#flask)
		3. [WikidataIntegrator](#wikidataintegrator)
		4. [Pytest](#pytest)
		5. [Travis](#travis)
		6. [Codacy](#codacy)
6. [Anexos](#anexos)
	1. [A. Pruebas](#a-pruebas)
		1. [A.1. Fase de diseño](#a1-fase-de-diseño)
		2. [A.2. Fase de implementación](#a2-fase-de-implementación)
	2. [B. Integración continua](#b-integración-continua)

<!-- /TOC -->

## Introducción
En este documento se presenta la documentación del módulo de sincronización - llamado a partir de ahora _hercules\_sync_ - entre ficheros de ontologías y un Triple-store, que forma parte de la Infraestructura Ontológica del proyecto Hércules.

## Alcance
El módulo _hercules\_sync_ se encarga de recibir actualizaciones de las ontologías y shapes que se encuentran almacenadas en un sistema de control de versiones. Cuando recibe una actualización, deberá procesar los cambios que se han realizado en las ontologías y/o shapes y reflejar estos cambios en el triple store en el que se encuentren almacenadas.

## Requisitos
A continuación se indican los requisitos de alto nivel identificados en la toma de requisitos del sistema. Éstos se encuentran divididos en requisitos funcionales y no funcionales:

### Requisitos funcionales
| Código        | Descripción          |
|:-------------:|:-------------|
| RF1      | El sistema establecerá un punto de entrada por el cuál recibir información sobre las actualizaciones de las ontologías. |
| RF2 | El sistema procesará la información recibida del CVS relativa a la actualización de las ontologías. |
| RF3 | El sistema detectará los cambios a realizar en el triple-store a partir de la información sobre las actualizaciones procesada.  |
| RF4 | El sistema se conectará con un triple-store para reflejar los cambios producidos en las ontologías. |
| RF5 | El sistema llevará a cambio la sincronización inversa: de cambios producidos en el triple-store a los ficheros con las ontologías. |
| RF6 | El sistema utilizará herramientas de logging para detectar anomalías en su funcionamiento. |

### Requisitos no funcionales
| Código        | Descripción          |
|:-------------:|:-------------|
| RNF1      | Seguridad: El sistema recibirá notificaciones de actualización del CVS de forma segura utilizando claves RSA. |
| RNF2      | Seguridad: El sistema actualizará el triple-store de forma segura a través del protocolo OAuth. |
| RNF3 | Compatibilidad: El sistema deberá funcionar como mínimo con las versiones 3.6, 3.7 y 3.8 del lenguaje de programación Python. |
| RNF4 | Mantenibilidad: La implementación del sistema seguirá el estándar de código PEP8. |
| RNF5 | Calidad: La cobertura de código de cada nueva versión será de al menos un 90%. |
| RNF6 | Extensibilidad: El sistema facilitará la utilización de distintos triple-stores donde almacenar las ontologías. |


## Diseño
En este apartado se especifica el diseño del módulo _hercules\_sync_. En primer lugar, se adjunta el diagrama de componentes del módulo, junto con una explicación de las responsabilidades de cada componente e interfaz que proporciona. A continuación, introducimos el diseño de las clases de cada componente a más bajo nivel, de nuevo acompañadas de explicaciones del funcionamiento de cada clase del sistema.

### Diagrama de componentes
Los componentes e interfaces detectados son los siguientes:
* listener: Este componente es el punto de entrada al subsistema por parte de otros sistemas externos. Para ello ofrece una interfaz al exterior, llamada OnWebhook, que es la encargada de recibir los datos sobre las actualizaciones de las ontologías por parte del CVS.
* ontology_synchronizer: Este componente realiza la sincronización de los cambios recibidos, creando operaciones a realizar en el triple_store para reflejar estos cambios. Ofrece una interfaz llamada _SynchronizeOntologies_, que es utilizada por el componente listener para sincronizar los cambios recibidos.
* diff_parser: El componente _diff\_parser_ se encarga de procesar la información del diff de los ficheros típica de los sistemas de control de versiones basados en Git. Ofrece una interfaz _ParseDiff_, que es utilizada por el componente _ontology\_synchronizer_ para obtener información detallada sobre los cambios en los ficheros de ontologías.
* triplestore_manager: Por último, el componente _triplestore\_manager_ se encarga de ejecutar las operaciones recibidas del componente _ontology\_synchronizer_ sobre el triple-store elegido. Para ello ofrece el interfaz _ExecuteModification_.

A continuación se muestra el diagrama de componentes del módulo:

### Diseño de clases
En esta sección vamos a mostrar el diseño de clases del módulo. Para facilitar la comprensión y lectura de las clases las hemos dividido en subsecciones correspondientes a cada uno de los componentes detectados en el apartado previo.

## Anexos
