# Virtual Cloth Assistant 👕✨

A web-based virtual clothing try-on application. This project provides an intuitive interface to upload a person's image and a garment image, and seamlessly generates a highly accurate visualization of the person wearing the garment.

## Features
- **Web Interface:** Clean and responsive frontend to easily upload images and view results.
- **Flask Backend:** A lightweight python server to handle image uploads and processing.
- **Hugging Face IDM-VTON API Integration:** Leverages the advanced IDM-VTON (Improving Diffusion Models for Virtual Try-on) model via the `gradio_client` API for highly accurate, realistic results.
- **Secure Token Authentication:** Uses Hugging Face API tokens (`HF_TOKEN`) to manage quota limits reliably.

## Prerequisites
- Python 3.8+
- A Google/GitHub account (for Git setup)
- A free Hugging Face API Access Token (`HF_TOKEN`)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shiva-Sai-369/Virtual-Cloth-Assistant.git
   cd Virtual-Cloth-Assistant
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install flask gradio_client huggingface_hub pillow requests
   ```

4. **Set your Hugging Face Token:**
   - Generate a free token from [Hugging Face Settings](https://huggingface.co/settings/tokens).
   - Set it as an environment variable in your terminal:
     - **Windows (PowerShell):** ` $env:HF_TOKEN="your_token_here" `
     - **Mac/Linux:** `export HF_TOKEN="your_token_here"`

## Usage

1. **Start the server:**
   ```bash
   python client-side/app.py
   ```
2. **Open your browser:**
   Navigate to `http://127.0.0.1:5000`

3. **Try it out:**
   Upload an image of a person, upload a garment image, and click "Try it" to see the magic happen!

## Architecture Highlights
The core logic resides in `client-side/app.py`, which securely routes requests from the browser to the Hugging Face Inference API instead of a heavy local ML model. It manages errors gracefully, authenticates the HTTP workspace environment automatically, and returns the AI-generated composite image to the user template (`client-side/templates/index.html`).
