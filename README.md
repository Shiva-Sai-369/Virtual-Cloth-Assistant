# Virtual Cloth Assistant 👕✨

A web-based virtual clothing try-on application. This project provides an intuitive interface to upload a person's image and a garment image, and seamlessly generates a highly accurate visualization of the person wearing the garment.

## Features
- **Web Interface:** Clean and responsive frontend to easily upload images and view results.
- **Flask Backend:** A lightweight python server to handle image uploads and processing.
- **Hugging Face IDM-VTON Integration:** Leverages the advanced IDM-VTON (Improving Diffusion Models for Virtual Try-on) model via the gradio_client API for highly accurate, realistic results.
- **Secure Token Authentication:** Uses Hugging Face API tokens to manage quota limits reliably.

## Prerequisites
- Python 3.8+
- A free Hugging Face Access Token (HF_TOKEN)

## Installation & Setup

1. **Clone the repository:**
   `ash
   git clone https://github.com/Shiva-Sai-369/Virtual-Cloth-Assistant.git
   cd Virtual-Cloth-Assistant
   `

2. **Create and activate a virtual environment:**
   `ash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   `

3. **Install the dependencies:**
   `ash
   pip install flask gradio_client huggingface_hub pillow requests werkzeug
   `

4. **Set your Hugging Face Token:**
   - Generate a free token from [Hugging Face Settings](https://huggingface.co/settings/tokens).
   - Set it as an environment variable in your terminal:
     - **Windows (PowerShell):** $env:HF_TOKEN="your_token_here"
     - **Mac/Linux:** export HF_TOKEN="your_token_here"

## Usage

1. **Start the server:**
   `ash
   python client-side/app.py
   `
2. **Open your browser:**
   Navigate to http://127.0.0.1:5000

3. **Try it out:**
   Upload a person's image and a garment image, then click the Try-on button.

## About
This project was customized to use server-side API routing via Hugging Face Spaces instead of local heavy GPU rendering, making it fast and lightweight for any machine.
