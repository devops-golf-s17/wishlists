Feature: The wishlists service back-end
    As a Wishlists Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists and the items in them


Background:
    Given the server is started
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


Scenario: List all wishlists
	When I visit "wishlists"
	Then I should see a wishlist with id "1"
	And I should see a wishlist with id "2"
	And I should see a wishlist with id "3"


Scenario: Get a wishlist with given id
    When I retrieve "wishlists" with id "1"
    Then I should see "user1" in this wishlist
    Then I should not see "404 Not Found"


    
Scenario: Deleting a wishlist
    When I visit "wishlists"
    Then I should see a wishlist with id "1" and name "wl1"
    And I should see a wishlist with id "2" and name "wl2"
    And I should see a wishlist with id "3" and name "wl3"
    When I delete "wishlists" with id "2"
    And I visit "wishlists"
    Then I should see a wishlist with id "1" and name "wl1"
    And I should not see a wishlist with id "2" and name "wl2"
    And I should see a wishlist with id "3" and name "wl3"


