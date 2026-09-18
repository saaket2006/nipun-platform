import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from backend.database.database import Base
from backend.models.enums import UserRole, CompanyType, ResumeStatus

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole, native_enum=False), nullable=True, default=UserRole.UNASSIGNED)
    profile_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="owner", cascade="all, delete-orphan")
    recruiter_profile = relationship("RecruiterProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    candidate_profile = relationship("CandidateProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

class RecruiterProfile(Base):
    __tablename__ = "recruiter_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    company_type = Column(SQLEnum(CompanyType, native_enum=False), nullable=False)
    hiring_domain = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="recruiter_profile")

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_status = Column(String(100), nullable=False)
    field_of_study = Column(String(255), nullable=False)
    current_domain = Column(String(255), nullable=False)
    resume_version_counter = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="candidate_profile")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    label = Column(String(255), nullable=True)
    label_source = Column(String(50), nullable=True)
    status = Column(SQLEnum(ResumeStatus, native_enum=False), default=ResumeStatus.ACTIVE, nullable=False)
    extracted_text = Column(Text, nullable=False)
    original_filename = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    candidate = relationship("User", back_populates="resumes")
    scan_results = relationship("ScanResult", back_populates="resume", cascade="all, delete-orphan")

class ScoringProfile(Base):
    __tablename__ = "scoring_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_role = Column(String(255), nullable=True)
    experience_level = Column(String(100), nullable=True)
    domain = Column(String(100), nullable=True)
    weights = Column(JSON, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    company = Column(String(255), nullable=True)
    optional_notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="job_descriptions")
    scan_results = relationship("ScanResult", back_populates="job_description", cascade="all, delete-orphan")

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    ats_score = Column(Float, nullable=False)
    analysis_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="scan_results")
    job_description = relationship("JobDescription", back_populates="scan_results")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")
