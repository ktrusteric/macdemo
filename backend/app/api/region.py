from fastapi import APIRouter
from app.utils.region_mapper import RegionMapper

router = APIRouter()

@router.get("/cities-details")
async def get_cities_details():
    cities = RegionMapper.get_all_cities()
    result = []
    for city in cities:
        info = RegionMapper.get_full_location_info(city)
        result.append({
            "city": info.get("city"),
            "province": info.get("province"),
            "region": info.get("region"),
            "province_code": info.get("province_code"),
            "region_code": info.get("region_code"),
        })
    return {"cities": result, "total": len(result)}

@router.get("/provinces")
async def get_provinces():
    return {"provinces": RegionMapper.get_all_provinces()}

@router.get("/regions")
async def get_regions():
    return {"regions": RegionMapper.get_all_regions()} 