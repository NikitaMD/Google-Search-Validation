##Small framework that can be used to automate Google Search
####It can do: 
- Execute searches for different keywords (supplied as command line parameters)
- Validate a link (supplied as command line parameters) 
- Compare total amount of the returns with expected (supplied as command line parameters)

The search should perform the following actions:
1.      Open a browser
2.      Go to the Google Search page (http://www.google.com)
3.      Enter one keyword or phrase (command line parameter: --kwd)
4.      Validate total amount with expected (command line parameter: --expected_total)
5.      Click on the (command line parameter: -- link_to_validate) result link
6.      Verify Web Page status codes (Must be 200)
7.      Capture the size of the page and site’s title
8.      Generate the report into report.txt

Example of running command:
`python google_search_validation.py --kwd "quality assurance" --link_to_validate 26 --expected_total 109000000`


# Author: Nikita Mader