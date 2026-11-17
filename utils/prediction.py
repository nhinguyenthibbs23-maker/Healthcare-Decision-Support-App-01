import joblib,numpy as np,pandas as pd,streamlit as st
from utils.data_loader import ROOT,meta
@st.cache_resource
def load_pipeline(): return joblib.load(ROOT/'models/pipeline.joblib')
def validate_input(values,m):
    if set(values)!=set(m['features']): raise ValueError('Please complete every question.')
    for c,v in values.items():
        if not isinstance(v,(int,float,np.number)) or not np.isfinite(v): raise ValueError('Invalid answer: '+c)
        lo,hi=m['valid_input_ranges'][c]
        if not lo<=v<=hi: raise ValueError(f'{c} must be between {lo:g} and {hi:g}.')
        if c in m['valid_values'] and v not in m['valid_values'][c]: raise ValueError('Unsupported value: '+c)
def predict(values):
    m=meta();validate_input(values,m)
    return float(load_pipeline().predict_proba(pd.DataFrame([values],columns=m['features']))[0,1])
