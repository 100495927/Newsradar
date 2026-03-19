from fastapi import FastAPI

app = FastAPI(title="NewsRadar Backend")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
