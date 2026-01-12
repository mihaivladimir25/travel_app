Travel Advisor – Smart Itinerary Planner with Elasticsearch



Travel Advisor is a Django web application that helps users discover tourist attractions inside a city, visualize them on an interactive map, perform fuzzy searches using Elasticsearch and generate optimized travel itineraries using real routing data.



The project demonstrates how distributed search engines can be integrated into a classical web architecture to significantly improve search quality and user experience.



Milestone 1 – Project Description



The idea of the project was to build an application that allows tourists to search attractions even when they do not remember the exact name. Classical SQL search fails in such scenarios. By integrating Elasticsearch, the application can understand misspelled queries and return relevant results.



The application offers an interactive map that displays attractions, allowing users to visualize their route and selected points.



Milestone 2 – Use Cases



The core use cases are searching attractions, filtering them by category, selecting them from a list, generating an itinerary between them and saving the itinerary to the user profile.



These use cases shaped the entire development process.



Milestone 3 – REST API and Swagger



A REST API was created for all critical operations such as search and itinerary generation. The API is fully documented using Swagger (OpenAPI) and can be accessed at:



http://127.0.0.1:8000/swagger/





Milestone 4 – Elasticsearch Mapping



Elasticsearch was deployed using Docker:



docker run -d --name travel-es -p 9200:9200 \\

&nbsp; -e "discovery.type=single-node" \\

&nbsp; -e "xpack.security.enabled=false" \\

&nbsp; elasticsearch:8.11.4





The mapping was created using:



{

&nbsp; "mappings": {

&nbsp;   "properties": {

&nbsp;     "name": { "type": "text" },

&nbsp;     "description": { "type": "text" },

&nbsp;     "city": { "type": "keyword" },

&nbsp;     "location\_type": { "type": "keyword" }

&nbsp;   }

&nbsp; }

}





Milestone 5 – Implementation



The fuzzy search logic is implemented using:



"multi\_match": {

&nbsp; "query": q,

&nbsp; "fields": \["name", "description"],

&nbsp; "fuzziness": "AUTO"

}





This allows the system to return British Museum when the user searches for birtish.



Milestone 6 – Postman Testing



All endpoints were tested using Postman.



Example request:



GET /api/search-locations/?q=birtish





Response:



\[

&nbsp; {

&nbsp;   "id": 2,

&nbsp;   "name": "British Museum",

&nbsp;   "city": "London",

&nbsp;   "type": "museum"

&nbsp; }

]





Conclusion



This project demonstrates how Elasticsearch enhances traditional web applications by providing intelligent fuzzy searching, fast indexing and scalable querying while maintaining a clean Django architecture.

