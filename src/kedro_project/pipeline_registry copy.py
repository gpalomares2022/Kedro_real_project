"""Project pipelines."""
from typing import Dict
import streamlit as st

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline


a= find_pipelines()    

st.title(a)
st.title("gabi")
 
