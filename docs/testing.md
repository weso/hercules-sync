![](../images/logos_feder.png)

# Testing BDD con Cucumber

## Configuración del entorno

Ver documento [README](https://github.com/HerculesCRUE/ib-asio-docs-/blob/master/entregables_hito_2/testing/testing.md) para la configuración de los tests.

## Escenarios

A continuación se describen los escenarios probados, utilizando el framework [Cucumber](https://cucumber.io/docs/cucumber/).

| Feature                                                     | Descripción                                                                                                                                          |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`change_triplestore.feature`](../tests/features/change_triplestore.feature)     | Caso de uso donde se comprueba que el sistema funciona con distintos triplestores.                                              |
| [`synchronize_rdf.feature`](../tests/features/synchronize_rdf.feature)           | Caso de uso donde se comprueba que el sistema es capaz de propagar los cambios que se realicen en la ontología al triple store elegido. En este caso wikibase.|
