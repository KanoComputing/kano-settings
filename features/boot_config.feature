# language: en
Feature: Settings reflected in the boot "config.txt" are updated correctly

    @wip
    Scenario Outline: Setting a resolution applies it only to the current screen
        Given A screen with EDID "<edid>" is plugged in
        And The resolution is <start_resolution>
        When The resolution is set to <end_resolution>
        Then Only the EDID "<edid>" entry is changed

        Examples:
            | edid       | start_resolution | end_resolution |
            | VSC-TD2220 |        1600x1200 |      1920x1080 |
            | AST-484848 |        1600x1200 |      1920x1080 |


    Scenario Outline: Setting a resolution for a new screen applies it only to the current screen
        Given No EDID screen information is created
        And A screen with EDID "<edid>" is plugged in
        And The resolution is <start_resolution>
        When The resolution is set to <end_resolution>
        Then The EDID "<edid>" entry is created
        And Only the EDID "<edid>" entry is changed

        Examples:
            | edid       | start_resolution | end_resolution |
            | VSC-TD2220 |        1600x1200 |      1920x1080 |
            | AST-484848 |        1600x1200 |      1920x1080 |


    Scenario: Setting the resolution works
    Scenario: Screen kit resolution is correctly set
