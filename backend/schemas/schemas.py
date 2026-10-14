from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from backend.models.enums import UserRole, CompanyType

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = Field(default=None)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    profile_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True

class RecruiterProfileResponse(BaseModel):
    id: int
    company_name: str
    company_type: CompanyType
    hiring_domain: str
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True

class CandidateProfileResponse(BaseModel):
    id: int
    current_status: str
    field_of_study: str
    current_domain: str
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True

class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    profile_completed: bool
    created_at: datetime
    recruiter_profile: Optional[RecruiterProfileResponse] = None
    candidate_profile: Optional[CandidateProfileResponse] = None

    class Config:
        from_attributes = True
        orm_mode = True

class CandidateProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    current_status: Optional[str] = Field(default=None, min_length=1, max_length=100)
    field_of_study: Optional[str] = Field(default=None, min_length=1, max_length=255)
    current_domain: Optional[str] = Field(default=None, min_length=1, max_length=255)

    @field_validator("display_name", "current_status", "field_of_study", "current_domain", mode="before")
    @classmethod
    def validate_and_strip(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be null")
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
            return stripped
        return v

class RecruiterProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    company_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    company_type: Optional[CompanyType] = None
    hiring_domain: Optional[str] = Field(default=None, min_length=1, max_length=100)

    @field_validator("display_name", "company_name", "hiring_domain", mode="before")
    @classmethod
    def validate_and_strip(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be null")
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
            return stripped
        return v

    @field_validator("company_type", mode="before")
    @classmethod
    def validate_company_type(cls, v):
        if v is None:
            raise ValueError("company_type cannot be null")
        return v

class OnboardingStatusResponse(BaseModel):
    profile_completed: bool
    role: Optional[UserRole] = None

class OnboardingSubmission(BaseModel):
    role: UserRole
    question_1: str = Field(..., min_length=1)
    question_2: str = Field(..., min_length=1)
    question_3: str = Field(..., min_length=1)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

class ResetPasswordResponse(BaseModel):
    message: str

class ScreeningTaskSummaryResponse(BaseModel):
    id: int
    role: str
    resume_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ScreeningTaskDetailResponse(BaseModel):
    id: int
    role: str
    job_description: str
    resume_count: int
    ranked_results: List[Any]
    created_at: datetime

    class Config:
        from_attributes = True

class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    name: str
    subtitle: Optional[str] = None
    description: str
    company: Optional[str] = None
    optional_notes: Optional[str] = None
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class JobDescriptionCreate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    description: str
    subtitle: Optional[str] = None
    company: Optional[str] = None
    optional_notes: Optional[str] = None

class JobDescriptionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    description: str
    subtitle: Optional[str] = None
    company: Optional[str] = None
    optional_notes: Optional[str] = None
