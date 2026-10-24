import pytest
from backend.services.info_extractor import extract_experience

def test_extract_experience_standard_formats():
    """Test extracting experience with standard variations."""
    assert extract_experience("I have 5 years of experience in Python.") == 5
    assert extract_experience("10+ years experience") == 10
    assert extract_experience("3 yrs experience") == 3
    assert extract_experience("1 yr of experience") == 1
    assert extract_experience("Worked for 7 years of experience in AI.") == 7

def test_extract_experience_multiple_mentions():
    """Test extracting the maximum experience when mentioned multiple times."""
    assert extract_experience("2 years of experience here, and 5 years of experience there") == 5
    assert extract_experience("Had 10 years experience before getting 2 more years experience.") == 10

def test_extract_experience_no_match():
    """Test when no experience is mentioned."""
    assert extract_experience("I just graduated.") == 0
    assert extract_experience("I worked at a company.") == 0
    assert extract_experience("Many years of working.") == 0

def test_extract_experience_edge_cases():
    """Test edge cases with formatting and spacing."""
    assert extract_experience("12 + years of experience") == 12
    assert extract_experience("4+yrs experience") == 4
    assert extract_experience("15+ years experience") == 15
    assert extract_experience("My 0 years of experience") == 0
    assert extract_experience("I have twenty years of experience") == 0  # Assuming it only captures digits based on regex

def test_extract_experience_case_insensitivity():
    """Test case insensitivity."""
    assert extract_experience("5 YEARS OF EXPERIENCE") == 5
    assert extract_experience("5 Years Of Experience") == 5
    assert extract_experience("5 Yrs Experience") == 5

from backend.services.info_extractor import extract_education, extract_name

def test_extract_education_remediation():
    # Negative cases (ordinary English words or tool names)
    assert extract_education("Contact me at...") == "None"
    assert extract_education("I will be...") == "None"
    assert extract_education("Skills: MS Excel, Python") == "None"
    assert extract_education("Proficient in MS Word and MS Office.") == "None"

    # Positive cases
    assert extract_education("Master of Engineering") == "Master"
    assert extract_education("M.E. Computer Science") == "Master"
    assert extract_education("M.E Computer Science") == "Master"
    assert extract_education("Bachelor of Engineering") == "Bachelor"
    assert extract_education("B.E. Computer Science") == "Bachelor"
    assert extract_education("B.E Computer Science") == "Bachelor"
    assert extract_education("M.S. Computer Science") == "Master"
    assert extract_education("Master of Science") == "Master"
    assert extract_education("MBA") == "Master"
    assert extract_education("B.Tech") == "Bachelor"
    assert extract_education("M.Tech") == "Master"

def test_extract_name_valid_and_invalid():
    # Valid names
    assert extract_name("John Doe\njohn@example.com") == "John Doe"
    assert extract_name("Saaket Kumar\nsaaket@example.com") == "Saaket Kumar"
    assert extract_name("Jane Smith\njane@example.com") == "Jane Smith"

    # Invalid headings / job titles (should not be extracted as name)
    assert extract_name("Software Engineer\njohn@example.com") == "Not Provided"
    assert extract_name("Full Stack Developer\njohn@example.com") == "Not Provided"
    assert extract_name("Professional Summary\nMotivated engineer...") == "Not Provided"
    assert extract_name("Skills\nPython, Docker") == "Not Provided"
    assert extract_name("Experience\nGoogle - 3 years") == "Not Provided"
    assert extract_name("Education\nMIT - 2022") == "Not Provided"

    # Name after a job title header
    resume_with_header = "SOFTWARE ENGINEER\nJohn Doe\njohn@example.com"
    assert extract_name(resume_with_header) == "John Doe"

from backend.services.info_extractor import extract_projects

def test_extract_projects_no_projects():
    """Test extracting projects when there is no mention of projects."""
    assert extract_projects("I have experience in Python.") == 0
    assert extract_projects("Just a regular resume.") == 0

def test_extract_projects_section_headers():
    """Test extracting projects with different section headers."""
    assert extract_projects("Some text\nProjects\nSome more text") == 3
    assert extract_projects("Some text\nPersonal Projects\nSome more text") == 3
    assert extract_projects("Some text\nAcademic Projects\nSome more text") == 3
    assert extract_projects("   Projects   \n") == 3
    assert extract_projects("  Personal Projects  \n") == 3
    assert extract_projects("Academic Projects\n") == 3

def test_extract_projects_project_counts():
    """Test extracting projects based on word count without header."""
    assert extract_projects("I worked on a project.") == 0
    assert extract_projects("I worked on a project and another project.") == 1
    assert extract_projects("project project project project") == 1
    assert extract_projects("project project project project project") == 2
    assert extract_projects("I have 6 projects: project 1, project 2, project 3, project 4, project 5") == 2

def test_extract_projects_combined_score():
    """Test extracting projects with both header and word counts, ensuring cap at 5."""
    assert extract_projects("Projects\nI did a project.") == 4  # Header (3) + 1 project word (0) - Wait, "Projects" in header is 1 word, "project" is 1 word. Total 2 words -> +1 score. So 3+1 = 4.
    assert extract_projects("Personal Projects\nProject 1\nProject 2\nProject 3\nProject 4") == 5 # Header (3) + 5 project words -> +2 score. So 3+2 = 5.
    assert extract_projects("Academic Projects\nProject Project Project Project Project Project") == 5 # Cap at 5.

def test_extract_projects_case_insensitivity():
    """Test case insensitivity for projects extraction."""
    assert extract_projects("PROJECTS\n") == 3
    assert extract_projects("PERSONAL PROJECTS\n") == 3
    assert extract_projects("ACADEMIC PROJECTS\n") == 3
    assert extract_projects("PrOjEcTs\n") == 3
    assert extract_projects("project PROJECT Project") == 1

def test_extract_projects_regex_boundaries():
    """Test word boundaries for project mentions."""
    assert extract_projects("projecting projector") == 0
    assert extract_projects("project projects") == 1
