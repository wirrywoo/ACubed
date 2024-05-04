#!/bin/bash

fastapi run ./fastapi/server.py & 
streamlit run ./streamlit/ui.py