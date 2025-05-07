from fastapi import APIRouter
from datetime import datetime, timedelta
from app.services.usgs import get_earthquake_data
from app.utils.state_coordinates import state_coordinates

router = APIRouter()

@router.get("/")
def home():
    return "Welcome to USGS"
    

@router.get("/v1/earthquakes/sf-bay-area")
async def get_sf_earthquakes(start_time:str, end_time:str, min_magnitude: float=2.0):
    params={
        "starttime":start_time,
        "endtime":end_time,
        "format":"geojson",
        "minmagnitude":min_magnitude,
        "latitude":"37.7749",
        "longitude":"-122.4194",
        "maxradiuskm":100
    }
    data= await get_earthquake_data(params)
    return data


@router.get("/v1/earthquakes/sf-bay-area/felt-reports")
async def get_sf_felt_reports(start_time:str, end_time:str, min_magnitude: float=2.0, min_felt: int=10):
    params={
        "starttime":start_time,
        "endtime":end_time,
        "format":"geojson",
        "minmagnitude":min_magnitude,
        "latitude":"37.7749",
        "longitude":"-122.4194",
        "maxradiuskm":100,
        "minfelt":min_felt
    }
    data= await get_earthquake_data(params)
    return data


@router.get("/v1/earthquakes/tsunami-alerts")
async def get_earthquake_with_tsunami_alerts(min_magnitude: float=2.0,state:str="California"):

    end_time = datetime.now().date()
    start_time=end_time-timedelta(1)

    if not state_coordinates.get(state):
        return "Invalid State. Please use state name as per https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States "

    params={
        "format":"geojson",
        "starttime": start_time.isoformat(),
        "endtime": end_time.isoformat(),
        "minmagnitude":min_magnitude,
        "latitude": state_coordinates[state]["lat"],
        "longitude":state_coordinates[state]["lon"],
        "maxradiuskm":250
       }

    data= await get_earthquake_data(params)

    # filter for earthquake that triggered tsunami alerts 

    filtered_data = [
        feature for feature in data['features']
        if feature['properties'].get('tsunami', 0) == 0  # Check if tsunami field is present and equals 1
    ]

    return {"count": len(filtered_data), "earthquakes": filtered_data}