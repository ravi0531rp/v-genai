from neo4j import GraphDatabase
import random
from datetime import datetime, timedelta

# Neo4j database connection details
URI = "bolt://localhost:7687"  
USER = "neo4j"  
PASSWORD = "password"  

# Create a driver instance
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# Sample data generation
def random_date(start_year=1940, end_year=2023):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def create_sample_data():
    people = [{"name": f"Person_{i}", "born": random_date().strftime("%Y-%m-%d")} for i in range(1, 31)]
    movies = [
        {"title": f"Movie_{i}", "tagline": f"Tagline for Movie_{i}", "released": random_date(1980, 2023).strftime("%Y-%m-%d")}
        for i in range(1, 101)
    ]
    return people, movies

def populate_db(driver, people, movies):
    with driver.session() as session:
        # Create nodes
        session.run("UNWIND $people AS person CREATE (:Person {name: person.name, born: person.born})", people=people)
        session.run("UNWIND $movies AS movie CREATE (:Movie {title: movie.title, tagline: movie.tagline, released: movie.released})", movies=movies)
        
        # Create random relationships
        for person in people:
            for _ in range(random.randint(1, 5)):
                target_person = random.choice(people)["name"]
                if target_person != person["name"]:
                    session.run("""
                        MATCH (p1:Person {name: $p1_name}), (p2:Person {name: $p2_name})
                        MERGE (p1)-[:FOLLOWS]->(p2)
                    """, p1_name=person["name"], p2_name=target_person)
            
            for _ in range(random.randint(1, 10)):
                movie = random.choice(movies)["title"]
                relationship = random.choice(["ACTED_IN", "DIRECTED", "WROTE", "PRODUCED", "REVIEWED"])
                session.run(f"""
                    MATCH (p:Person {{name: $person_name}}), (m:Movie {{title: $movie_title}})
                    MERGE (p)-[:{relationship}]->(m)
                """, person_name=person["name"], movie_title=movie)

# Generate and populate the database
if __name__ == "__main__":
    people, movies = create_sample_data()
    populate_db(driver, people, movies)
    print("Database populated successfully!")
