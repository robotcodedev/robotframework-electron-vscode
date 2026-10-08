*** Settings ***
Resource            ../resources/fixture.resource

Suite Setup         Start Fixture App    --started-in-suite-setup


*** Test Cases ***
Application From Suite Setup Is Open In First Test
    Get Title    ==    Electron Fixture

Application From Suite Setup Is Still Open In Second Test
    Fixture App Is Running    --started-in-suite-setup
    Get Title    ==    Electron Fixture
