from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from pprint import pprint
from scipy.stats import norm, invgamma
from utils import *
from constants import *
from API import *
from ML import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import re

%matplotlib inline