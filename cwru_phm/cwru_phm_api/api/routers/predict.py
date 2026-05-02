import numpy as np
from fastapi import APIRouter, HTTPException, Request

from api.core.model import FaultClassifier
from api.schemas.common import (
    DiagnosisOut,
    EnvelopeFeatures,
    FaultFrequenciesOut,
    FeatureBlockOut,
    FreqFeatures,
    TimeFeatures,
)
from api.schemas.predict import (
    MetaOut,
    PredictionOut,
    PredictRequest,
    PredictResponse,
)

router = APIRouter(tags=["predict"])


def _build_response(req: PredictRequest, classifier: FaultClassifier) -> PredictResponse:
    signal_arr = np.asarray(req.signal, dtype=np.float64)

    try:
        result = classifier.predict(signal_arr, fs=req.fs, rpm=req.rpm)
    except ValueError as e:
        # 길이 불일치 등 입력 문제
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    f = result.features
    ff = result.fault_freq
    d = result.diagnosis

    return PredictResponse(
        prediction=PredictionOut(
            label=result.label,
            class_id=result.class_id,
            probabilities=result.probabilities,
        ),
        features=FeatureBlockOut(
            time_domain=TimeFeatures(
                RMS=f.RMS, Kurtosis=f.Kurtosis, Crest=f.Crest,
                P2P=f.P2P, Skewness=f.Skewness, Std=f.Std,
            ),
            freq_domain=FreqFeatures(
                FFT_0_200=f.FFT_0_200,
                FFT_200_500=f.FFT_200_500,
                FFT_2k_5k=f.FFT_2k_5k,
            ),
            envelope=EnvelopeFeatures(
                Env_BPFO=f.Env_BPFO, Env_BPFI=f.Env_BPFI, Env_BSF=f.Env_BSF,
                Env_0_200=f.Env_0_200, Env_200_500=f.Env_200_500,
            ),
        ),
        diagnosis=DiagnosisOut(
            dominant_peak_hz=d.dominant_peak_hz,
            dominant_peak_amp=d.dominant_peak_amp,
            snr=d.snr,
            nearest_fault=d.nearest_fault,
            nearest_fault_freq_hz=d.nearest_fault_freq_hz,
            delta_hz=d.delta_hz,
        ),
        fault_frequencies=FaultFrequenciesOut(
            rpm=ff.rpm, fr=ff.fr,
            BPFO=ff.BPFO, BPFI=ff.BPFI,
            BSF=ff.BSF, two_BSF=ff.two_BSF, FTF=ff.FTF,
        ),
        meta=MetaOut(
            model_version=classifier.meta.get("model_version"),
            inference_ms=result.inference_ms,
            segment_length=len(signal_arr),
            fs=req.fs,
            rpm=req.rpm,
        ),
    )


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, request: Request) -> PredictResponse:
    classifier: FaultClassifier = request.app.state.classifier
    return _build_response(req, classifier)
