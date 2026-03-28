from flask import Flask, request, render_template
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO
import base64
import os
import tempfile
import time

try:
    from gradio_client import Client, handle_file
except ImportError:
    Client = None
    handle_file = None

try:
    from huggingface_hub import login as hf_login
except ImportError:
    hf_login = None

app = Flask(__name__)

_hf_client = None
_hf_logged_in = False


def _get_hf_client():
    global _hf_client
    if _hf_client is None:
        if Client is None:
            raise RuntimeError("gradio_client is not installed")
        space_id = os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")
        _hf_client = Client(space_id)
    return _hf_client


def _build_hf_client(space_id):
    global _hf_logged_in
    if Client is None:
        raise RuntimeError("gradio_client is not installed")
    hf_token = os.getenv("HF_TOKEN", "").strip()
    if hf_token and hf_login is not None and not _hf_logged_in:
        hf_login(token=hf_token, add_to_git_credential=False)
        _hf_logged_in = True
    return Client(space_id)


def _call_direct_backend(url, cloth_file, model_file):
    response = requests.post(
        url=url,
        files={
            "cloth": (cloth_file[0], BytesIO(cloth_file[1]), cloth_file[2]),
            "model": (model_file[0], BytesIO(model_file[1]), model_file[2]),
        },
        timeout=120,
    )
    response.raise_for_status()
    op = Image.open(BytesIO(response.content))
    op.load()
    return op, "Generated using the configured VTON backend."


def _call_hf_idm_vton(cloth_file, model_file):
    configured_spaces = os.getenv("HF_SPACE_CANDIDATES", "").strip()
    if configured_spaces:
        space_ids = [s.strip() for s in configured_spaces.split(",") if s.strip()]
    else:
        space_ids = [os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")]

    max_retries = int(os.getenv("HF_MAX_RETRIES", "3"))
    last_error = None
    attempt_errors = []

    with tempfile.TemporaryDirectory() as td:
        model_path = os.path.join(td, model_file[0] or "model.jpg")
        cloth_path = os.path.join(td, cloth_file[0] or "cloth.jpg")

        with open(model_path, "wb") as fp:
            fp.write(model_file[1])
        with open(cloth_path, "wb") as fp:
            fp.write(cloth_file[1])

        person = {
            "background": handle_file(model_path),
            "layers": [],
            "composite": None,
        }

        for attempt in range(max_retries):
            space_id = space_ids[attempt % len(space_ids)]
            try:
                client = _build_hf_client(space_id)

                result = client.predict(
                    dict=person,
                    garm_img=handle_file(cloth_path),
                    garment_des="upper body clothing",
                    is_checked=True,
                    is_checked_crop=False,
                    denoise_steps=20,
                    seed=42,
                    api_name="/tryon",
                )

                output_path = result[0] if isinstance(result, (tuple, list)) else result
                op = Image.open(output_path)
                op.load()
                return op, f"Generated using Hugging Face VTON backend ({space_id})."
            except Exception as exc:  # noqa: BLE001 - external SDK/network can raise many exception types.
                last_error = exc
                message = str(exc)
                if len(message) > 140:
                    message = message[:140] + "..."
                attempt_errors.append(
                    f"attempt {attempt + 1} on {space_id}: {type(exc).__name__} - {message}"
                )
                # Free spaces are often cold-started; a short backoff improves reliability.
                time.sleep(min(2 + attempt, 5))

    details = "; ".join(attempt_errors) if attempt_errors else "unknown error"
    raise RuntimeError(f"HF backend failed after retries: {details}") from last_error


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/preds", methods=['POST'])
def submit():
    cloth = request.files.get('cloth')
    model = request.files.get('model')

    if not cloth or not model or not cloth.filename or not model.filename:
        return render_template('index.html', error="Please upload both cloth and model images.")

    cloth_file = (
        cloth.filename,
        cloth.read(),
        cloth.mimetype or "application/octet-stream",
    )
    model_file = (
        model.filename,
        model.read(),
        model.mimetype or "application/octet-stream",
    )

    provider = os.getenv("VTON_PROVIDER", "hf_idm_vton").lower()
    url = os.getenv("TRANSFORM_API_URL", "http://e793-34-123-73-186.ngrok-free.app/api/transform")

    # Validate inputs early to keep responses predictable and explainable in demos.
    try:
        Image.open(BytesIO(cloth_file[1])).verify()
        Image.open(BytesIO(model_file[1])).verify()
    except UnidentifiedImageError:
        return render_template('index.html', error="Uploaded files must be valid images (PNG/JPG).")

    try:
        if provider == "direct":
            op, info = _call_direct_backend(url, cloth_file, model_file)
        elif provider == "hf_idm_vton":
            try:
                op, info = _call_hf_idm_vton(cloth_file, model_file)
            except RuntimeError:
                # Optional failover to direct backend only when user explicitly configures it.
                if "TRANSFORM_API_URL" in os.environ:
                    op, info = _call_direct_backend(url, cloth_file, model_file)
                    info = f"{info} (HF failed, used direct backend failover)"
                else:
                    raise
        else:
            return render_template(
                'index.html',
                error="Unsupported VTON_PROVIDER. Use 'hf_idm_vton' or 'direct'.",
            )
    except (requests.RequestException, UnidentifiedImageError, RuntimeError, OSError, ValueError) as exc:
        err_text = str(exc)
        if "ZeroGPU quota" in err_text or "daily ZeroGPU quotas" in err_text:
            return render_template(
                'index.html',
                error=(
                    "Hugging Face anonymous quota is exhausted. Create a free HF token and set HF_TOKEN, "
                    "then restart the app."
                ),
            )

        short_reason = str(exc)
        if len(short_reason) > 220:
            short_reason = short_reason[:220] + "..."
        return render_template(
            'index.html',
            error=f"Try-on backend failed. {short_reason}",
        )

    buffer = BytesIO()
    op.save(buffer, 'png')
    buffer.seek(0)

    data = buffer.read()
    data = base64.b64encode(data).decode()

    return render_template('index.html', op=data, info=info)
    # return render_template('index.html', test=True)

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
