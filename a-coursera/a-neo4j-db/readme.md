## STEPS

1. Run Docker Container
```sh
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```
1. If issues

```sh
docker stop neo4j
docker rm neo4j

docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4JLABS_PLUGINS='["apoc"]' \
  -e NEO4J_dbms_security_procedures_unrestricted=apoc.* \
  neo4j:latest


```

2. Go to [browser](http://localhost:7474/browser/)

3. Login using credentials

4. Run the below in browser shell
```sh
RETURN 'Hello, Neo4j!' AS message;
```
5. Run the create_movies_db.py script tp populate the db.

6. Work in the check_movies.ipynb to explore.