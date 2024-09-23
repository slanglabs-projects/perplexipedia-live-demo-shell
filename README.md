# Perplexipedia Live Demo Steps

## Get perplexipedia running locally
1. Clone the repository
2. Install the dependencies -- ```pip3 install -r requirements.txt```
3. Run the streamlit app -- ```streamlit run main.py```
4. Open the browser and go to the URL shown in the terminal
5. Enter an input query and click on the "Get the answer" button. Nothing should happen.

## Create an AI Assistant using Conva.AI
1. Go to [Conva.AI](https://studio.conva.ai/)
2. Create an assistant with the following details:
    - Name: Perplexipedia
    - Description: An AI assistant that answers questions from Wikipedia
    - Capability: Wikipedia Q&A
    - Capability outline: 
    > This capability is called "wikipedia_qa". You will be given a list of documents from Wikipedia that are most likely to contain the answer to the user's question. You should provide an answer to the user's query based on the documents provided to you. If the given documents do not provide the right answer to the question, or if there are no documents, you must mention that you cannot provide an answer since wikipedia does not contain the answer to the question. Never make up an answer that is not available in the documents.  The "message" parameter must include the answer to the question, along with citations to the wikipedia documents. The "sources" parameter should include a list of URLs corresponding to the cited Wikipedia sources. The only parameters are "message", "sources" and "related_queries" and all are mandatory.
    > 
    > IMPORTANT: Each response must contain citations and the citations should be included in square brackets and have a prefix "cit". For example: "this is a sample response [cit1, cit3]"
3. Create a knowledge source for wikipedia (https://en.wikipedia.org) and connect it to all the parameters of the capability.
4. Create the Assistant and test it using the playground.
5. Go to the integration section and get the Assistant ID and API key and paste it at the appropriate place in `main.py`.
6. Reload the streamlit app and enter an input query and click on the "Get the answer" button. You should now see the answer to the query along with the citations and related queries.