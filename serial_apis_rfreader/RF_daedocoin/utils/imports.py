import os
import logging
import math
import asyncio
import serial
import sys
import json
import time
import configparser
import serial.tools.list_ports as sp
from typing import Optional
import datetime as dt
import csv

import uvicorn
from fastapi import HTTPException,APIRouter, status
import datetime as dt
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel