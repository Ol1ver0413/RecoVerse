import sys
import os
sys.path.append('')

from recoverse.workforce.society import UserBusinessRecommender
from camel.embeddings import SentenceTransformerEncoder

if __name__ == "__main__":
    examples = [
    ('Looking for a sushi restaurant downtown.', 'Jimmy'),
    ('I need a gym with personal trainers nearby.', 'Monera'),
    ('Can you find a pet store that sells organic food?', 'Elizabeth'),
    ('I want to get a haircut and maybe some styling done.', 'Jacque'),
    ('Need someone to fix my car’s engine and check the tires.', 'David'),
    ('Planning to relax with a massage this weekend.', 'Michelle'),
    ('Searching for a coffee shop or bakery open late.', 'Brian'),
    ('I have to visit the dentist and also get a facial.', 'Keny'),
    ('Looking for something fun to do with kids this Saturday.', 'Leonel'),
    ('I’m craving some food before catching a movie.', 'Russell'),
    ('Just wandering around, no specific plans.', 'Talia'),
    ('Not sure what I want, just exploring options.', 'Susan'),
    ('Need a daycare center that accepts infants.', 'Chantelle'),
    ('Looking for a 24-hour pharmacy nearby.', 'Andrew'),
    ('Want to find a place to learn painting classes.', 'Harry'),
    ]

    db_config = {
        'host': ,
        'port': ,
        'user': ',
        'password': ,
        'database': '
    }

    embed_model = SentenceTransformerEncoder(model_name="")

    recommender = UserBusinessRecommender(
        db_config=db_config,
        embed_model=embed_model
    )

    result = recommender.recommend(username=examples[0][1], query=examples[0][0])
    print("[推荐结果]：")
    print(result)

