Feature: The wishlists service back-end
    As a Wishlists Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists and the items in them


Background:
    Given the server is started

Scenario: The wishlists service is running
    When I visit the "home page"
    Then I should see "Wishlists REST API Service"
    Then I should not see "404 Not Found"


Scenario: List all wishlists
	When I visit "wishlists"
	Then I should see a wishlist with id "1"
	And I should see a wishlist with id "2"
	And I should see a wishlist with id "3"
	

