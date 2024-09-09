from typing import Any
from neo4j import GraphDatabase
import jieba.analyse
import jieba

class KnowledgeRetriever:
    def __init__(self):
        self.driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "YourPassword"))
        self.jieba_init()

    def jieba_init(self):
        jieba.initialize()
        jieba.load_userdict("./dict/disease.txt")
        jieba.load_userdict("./dict/symptoms.txt")
        jieba.load_userdict("./dict/department.txt")

    def execute_query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [record for record in result]

    def retrieve_str(self, text):
        wordList = jieba.analyse.extract_tags(text, topK=3)
        return self.retrieve(list(wordList))

    def retrieve(self, wordList):
        # query = f"""
        # WITH {wordList} AS wordList
        # MATCH (n)-[r:acompany_with|has_symptom|belongs_to*1..1]->(m)
        # WHERE ANY(word IN wordList WHERE n.name CONTAINS word)
        # RETURN DISTINCT n, r, m
        # UNION
        # WITH {wordList} AS wordList
        # MATCH (m)-[r:acompany_with|has_symptom|belongs_to*1..1]->(n)
        # WHERE ANY(word IN wordList WHERE n.name CONTAINS word)
        # RETURN DISTINCT n, r, m
        # """

        query = f"""
WITH {wordList} AS wordList
MATCH (n)
WITH n, wordList
UNWIND wordList AS word 
WITH n, word, apoc.text.levenshteinSimilarity(toString(n.name), word) AS similarity
WHERE similarity IS NOT NULL
WITH n, max(similarity) AS avgSimilarity
WHERE avgSimilarity > 0.5
WITH n,avgSimilarity  AS avgSimilarity
ORDER BY avgSimilarity DESC
LIMIT 5


MATCH (n)-[r:acompany_with|has_symptom|belongs_to*1..1]-(m)
RETURN DISTINCT n, r, m  
""".format(wordList=wordList)
        result = self.execute_query(query)
        return result
    
    #静态方法 print_record
    @staticmethod
    def print_record(record):
        relationships = record["r"]
        for relationship in relationships:
            start_node = relationship.start_node
            end_node = relationship.end_node
            print(f"{start_node['name']} {relationship.type} {end_node['name']}")

    @staticmethod
    def records_to_str(records):
        result = ""
        for record in records[:min(50, len(records))]:
            relationships = record["r"]
            for relationship in relationships:
                start_node = relationship.start_node
                end_node = relationship.end_node
                result += f"{start_node['name']} {relationship.type} {end_node['name']}\n"
        return result


if __name__ == "__main__":
    retriever = KnowledgeRetriever()
    text = "你好"
    print(list(jieba.analyse.extract_tags(text, topK=2)))
    result = retriever.retrieve_str(text)
    print(KnowledgeRetriever.records_to_str(result))
