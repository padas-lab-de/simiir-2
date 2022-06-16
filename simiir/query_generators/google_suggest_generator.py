from simiir.query_generators.base_generator import BaseQueryGenerator
import requests
import urllib.parse

class GoogleSuggestGenerator(BaseQueryGenerator):
    """
    A query generator that selects candidate queries from the Google Search Suggest API.
    """
    def __init__(self, stopword_file, background_file=[], max_depth=5):
        super(GoogleSuggestGenerator, self).__init__(stopword_file, background_file=background_file)
        self.__max_depth = max_depth
    
    def generate_query_list(self, search_context):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """

        topic = search_context.topic.title
        generated_queries = [(topic, 1)]

        for i in range(1, self.__max_depth):
            response = requests.get('https://suggestqueries.google.com/complete/search?&output=firefox&hl=en&gl=us&q=' + urllib.parse.quote_plus(generated_queries[-1][0]))
            suggestions_web = response.json()
            queries = suggestions_web[1]
            if len(queries) < 2:
                break
            generated_queries.append((queries[1], 1))

        return generated_queries
