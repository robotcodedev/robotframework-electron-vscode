*** Settings ***
Documentation       Waiting for elements, conditions, the network and promises in a window of an application.
Resource            ../resources/fixture.resource

Suite Setup         Start Fixture App    --page\=keywords.html
Suite Teardown      Close Browser    ALL


*** Test Cases ***
Elements And Conditions
    Go To Keywords Page
    Click    id=show-later
    Wait For Elements State    id=later    visible
    Wait For Condition    Element Count    id=later    ==    1
    Wait For Function    () => document.getElementById('later') !== null
    Wait For Load State    load

Network
    ${url} =    Web Server Url
    Go To    ${url}
    ${response} =    Promise To    Wait For Response    **/api
    ${request} =    Promise To    Wait For Request    **/api
    Click    id=load
    Wait For All Promises
    ${response} =    Wait For    ${response}
    Should Be Equal    ${response}[status]    ${200}
    Get Text    id=result    ==    {"answer": 42}
    ${http} =    Http    ${url}api
    Should Be Equal    ${http}[body]    ${{ {"answer": 42} }}

Navigation
    ${url} =    Web Server Url
    Go To Keywords Page
    ${promise} =    Promise To    Wait For Navigation    ${url}
    Go To    ${url}
    Wait For    ${promise}
    Go Back
    Get Title    ==    Keywords
    Go Forward
    Get Url    ==    ${url}

Timeouts And Retries
    Go To Keywords Page
    Set Browser Timeout    1s    scope=Test
    Run Keyword And Expect Error    *Timeout 1000ms exceeded*    Wait For Elements State    id=never    visible
    Set Retry Assertions For    1s    scope=Test
    Run Keyword And Expect Error    *should be*    Get Text    id=heading    ==    Something else


*** Keywords ***
Go To Keywords Page
    ${app} =    Get Fixture App
    Go To    file://${app}/keywords.html
