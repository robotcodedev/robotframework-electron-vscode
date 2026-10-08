*** Settings ***
Resource            ../resources/fixture.resource



*** Test Cases ***
Application Started In A Test
    Start Fixture App    --started-in-test
    Fixture App Is Running    --started-in-test

Application From Previous Test Has Ended
    Fixture App Has Exited    --started-in-test

Close Context Ends The Application
    Start Fixture App    --close-context
    Close Context
    Fixture App Has Exited    --close-context
