from fastapi import APIRouter, HTTPException
from models.schemas import UserResponse
from db import supabase

router = APIRouter()

@router.get("/user/{uuid}", response_model=UserResponse)
async def get_user(uuid: str):
    try:
        response = supabase.table("users").select("*").eq("uuid", uuid).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**response.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/{uuid}")
async def delete_user(uuid: str):
    try:
        response = supabase.table("users").delete().eq("uuid", uuid).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 