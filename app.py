from flask import Flask, render_template, request, Response, json, jsonify
from routers.seatgeek import getSeatGeekData
from modules.event import Event
import routers.mongo as Database

print(getSeatGeekData('miami', 30))