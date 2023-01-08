# TSW_RoutePlanner

**Description**\
A Route Planning Tool for the TSW Dispatch Function.

**Features**\
Iteracts with the GoMotive Api, extract trip data, and generates a google map route planner.

**Installation**\
`pip install requests`\
`pip install selenium`


**To Run**\
Create 3 text files: `chrome_profile.txt`, `Token.txt`,`TSW_Token.txt`\
Store `executable_path` of the chromedriver into `chrome_profile.txt`\
Store `X-Internal-Api-Key` into `Token.txt`\\ 
TSW's private token into `TSW_Token.txt`\
To run the program, run: `python RoutePlanner.py`\
In the Motive App, open `Dispatch` tab, select a trip and click `Share` to get the dispatch instance.


