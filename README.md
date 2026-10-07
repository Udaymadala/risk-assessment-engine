Set-Content README.md @"
# Enterprise Risk Assessment & Heatmap Engine 🛡️

An interactive risk assessment dashboard designed to evaluate, calculate, and visualize Inherent vs. Residual risk scores using the NIST SP 800-30 framework and ISO/IEC 27001:2022 standards.

## Key Features
<img width="2830" height="1634" alt="image" src="https://github.com/user-attachments/assets/5509e3dd-edda-4593-88f0-25b87583e653" />

- **5×5 Likelihood × Impact Matrix**: Calculates semi-quantitative risk scores and dynamic residual risk reduction based on selected compensating controls.
- **Interactive Heatmap**: Rendered in Plotly with directional mitigation vector mapping.
- **Document Generation**: Includes an ISO 27001:2022 ISMS risk assessment report exporter via python-docx.

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
