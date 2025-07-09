from models.models import Trail

trails_db = [
    Trail(
        id=1,
        name="Mont Blanc",
        location="Chamonix, France",
        latitude=45.8326,
        longitude=6.8652,
        elevation=4809,
        difficulty="Expert",
        description="The highest peak in Western Europe"
    ),
    Trail(
        id=2,
        name="Matterhorn Base Camp",
        location="Zermatt, Switzerland",
        latitude=45.9763,
        longitude=7.6586,
        elevation=3260,
        difficulty="Intermediate",
        description="Scenic trail to Matterhorn base camp"
    )
]

def get_all_trails():
    return trails_db