from fastapi import FastAPI


app = FastAPI(title="Purdue CS Degree Planner API")


@app.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok"}
