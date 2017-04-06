Feature: The wishlists service back-end
    As a Wishlists Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists and the items in them


Background:

    Given the following wishlists
        | id | name       | user_id |
        |  1 | wl1        | user1   |
        |  2 | wl2        | user2   |
        |  3 | wl3        | user3   |

    Given the following items
        | item_id | wishlist_id | description |
        | item1   | 1           | test item 1 |
        | item2   | 1           | test item 2 |
        | item3   | 2           | test item 3 |


Scenario: The wishlists service is running
    When I visit the "home page"
    Then I should see "Wishlists REST API Service"
    Then I should not see "404 Not Found"

