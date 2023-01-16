# TSW_RoutePlanner

**Description**\
A Route Planning Tool for TORONTO SUN WAH TRADING LTD and PLANWAY POULTRY INC.

**Features**\
Iteracts with the GoMotive Api, extract trip data, and generates a google map route planner.

**Installation**\
`pip install requests`\
`pip install selenium`\
`pip install webdriver_manager`


**To Run**\
Create 2 text files: `Token.txt`,`TSW_Token.txt`\
DO NO SHARE THESE FILES! \
Store `X-Internal-Api-Key` into `Token.txt` \
Store `X-Api-Key` into `TSW_Token.txt`\
To run the program, run: `python RoutePlanner.py`\
In the Motive App, open `Dispatch` tab, select a trip and click `Share` to get the dispatch instance.


