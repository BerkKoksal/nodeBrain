from fastapi import APIRouter, HTTPException
from services.neo4j_ingest import ingest_roadmap_into_neo4j

router = APIRouter()

@router.post("/generate-roadmap")
def generate_roadmap_endpoint(data: dict):
    learning_goal = data.get("goal")
    user_id = data.get("user_id", "user123")  # for now

    if not learning_goal:
        raise HTTPException(status_code=400, detail="Missing learning goal.")

    result = ingest_roadmap_into_neo4j(learning_goal, user_id)

    return result