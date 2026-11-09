from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone

from backend.app.database import db_manager
from backend.app.models.user import UserRegisterRequest, UserLoginRequest, UserProfileResponse, TokenResponse
from backend.app.auth.security import hash_password, verify_password
from backend.app.auth.jwt_handler import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest):
    users_col = db_manager.get_collection("users")
    
    # Check if username or email exists
    existing_user = await users_col.find_one({"username": req.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = await users_col.find_one({"email": req.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "username": req.username,
        "email": req.email,
        "hashed_password": hash_password(req.password),
        "full_name": req.full_name,
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    insert_res = await users_col.insert_one(user_doc)
    user_id = str(insert_res.inserted_id)

    token = create_access_token({"sub": req.username, "role": "user"})
    profile = UserProfileResponse(
        id=user_id,
        username=req.username,
        email=req.email,
        full_name=req.full_name,
        role="user",
        saved_vehicles_count=0,
        recommendations_count=0,
        created_at=user_doc["created_at"]
    )
    return TokenResponse(access_token=token, user=profile)

@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest):
    users_col = db_manager.get_collection("users")
    user = await users_col.find_one({"username": req.username})
    if not user or not verify_password(req.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id = str(user.get("_id"))
    token = create_access_token({"sub": user["username"], "role": user.get("role", "user")})

    saved_count = await db_manager.get_collection("saved_vehicles").count_documents({"user_id": user_id})
    rec_count = await db_manager.get_collection("recommendations").count_documents({"user_id": user_id})

    profile = UserProfileResponse(
        id=user_id,
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name", user["username"]),
        role=user.get("role", "user"),
        saved_vehicles_count=saved_count,
        recommendations_count=rec_count,
        created_at=user.get("created_at")
    )
    return TokenResponse(access_token=token, user=profile)

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    saved_count = await db_manager.get_collection("saved_vehicles").count_documents({"user_id": user_id})
    rec_count = await db_manager.get_collection("recommendations").count_documents({"user_id": user_id})

    return UserProfileResponse(
        id=user_id,
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user.get("full_name", current_user["username"]),
        role=current_user.get("role", "user"),
        saved_vehicles_count=saved_count,
        recommendations_count=rec_count,
        created_at=current_user.get("created_at")
    )
