from fastapi import APIRouter, Request

router = APIRouter(tags=["meta"])


@router.get("/health")
def health(request: Request) -> dict:
    classifier = getattr(request.app.state, "classifier", None)
    return {
        "status": "ok",
        "model_loaded": classifier is not None,
    }


@router.get("/model/info")
def model_info(request: Request) -> dict:
    classifier = request.app.state.classifier
    return classifier.info()
