#!/bin/bash

fastapi run ./api/server.py & 
streamlit run ./ui/app.py