from typing import List, Optional
from pydantic import BaseModel, Field

# CoFunding 和 SupportingDocument 模型通常也需要更健壮的定义
# 我们可以给它们的所有字段都加上默认值，以防万一

class ProjectDate(BaseModel):
    """A structured model to represent a date with optional month and day."""
    year: Optional[int] = Field(default=None, description="The year of the date.")
    month: Optional[int] = Field(default=None, description="The month of the date (as a number 1-12).")

class FundingSource(BaseModel):
    source: Optional[str] = Field(default=None, description="The name of the organization providing the funds.")
    amount: Optional[float] = Field(default=None, description="The amount of funding from this source.")

class CoFunding(BaseModel):
    is_mentioned: bool = Field(default=False)
    total_amount: Optional[float] = Field(default=None, description="The total sum of all co-funding amounts mentioned.")
    sources: Optional[List[FundingSource]] = Field(
        default=None,
        description="A detailed list of all co-funding sources, including who provided the funds and how much."
    )

class SupportingDocument(BaseModel):
    cv_attached: bool = Field(default=False, description="Is a CV or resume mentioned as an attachment?")
    portfolio_provided: bool = Field(default=False, description="Is a portfolio or work samples mentioned?")
    portfolio_url: Optional[str] = Field(default=None, description="If a URL for a portfolio is provided, extract the full link here.")
    letters_of_intent_attached: bool = Field(default=False, description="Are any Letters of Intent from partners mentioned?")
    partner_agreements_attached: bool = Field(default=False, description="Are any formal agreements with partners mentioned?")

class Application(BaseModel):
    # 1. Basic Formalities
    applicant_name: Optional[str] = Field(default=None, description="The full name of the individual or organization applying.")
    applicant_type: Optional[str] = Field(default=None, description="The type of applicant, e.g., 'Individual' or 'Organization'.")
    requested_amount: Optional[float] = Field(default=None, description="The total amount of funding requested in the application's currency.")
    project_duration: Optional[str] = Field(default=None, description="The total duration of the project, e.g., '24 months' or '1 year'.")
    work_basis: Optional[str] = Field(
        default=None,
        description="The work basis of the project. Extract if it's mentioned as 'full-time', 'part-time', etc. If not mentioned, leave as null."
    )
    project_start_date: Optional[ProjectDate] = Field(
        default=None,
        description="The proposed structured start date of the project. Extract the year and month."
    )
    project_end_date: Optional[ProjectDate] = Field(
        default=None,
        description="The proposed structured end date of the project. Extract the year and month."
    )
    main_artistic_field: Optional[str] = Field(default=None, description="The primary artistic discipline of the project, e.g., 'Visual Arts', 'Music', 'Literature'.")

    # 2. Core Project Elements
    main_goal_or_output: Optional[str] = Field(default=None, description="Summarize the main artistic output into a very short, title-like phrase, under 10 words. Focus only on WHAT will be created (e.g., 'three bronze sculptures about tides'). Do NOT extract the full descriptive sentence.")
    location: Optional[str] = Field(default=None, description="Extract the primary and final installation location of the artwork. Look for keywords like 'install', 'exhibit', 'place in', or 'unveil at'. Prioritize specific venues like parks, museums, or galleries over general geographical regions. If multiple locations are mentioned, select the one where the final piece will be permanently displayed.")
    target_audience: Optional[str] = Field(default=None, description="A description of the primary group of people the project aims to reach or serve.")
    community_engagement_methods: Optional[List[str]] = Field(default=None, description="A list of methods for public interaction, e.g., 'Workshops', 'Public casting events'.")

    # 3. Resources & Feasibility
    detailed_budget_provided: bool = Field(default=False, description="Indicates whether a detailed cost breakdown is included in the application.")
    co_funding: Optional[CoFunding] = Field(default=None, description="Details regarding co-funding from other sources.")
    partners: Optional[List[str]] = Field(default=None, description="List all external organizations involved in the project. If an organization is mentioned as the location for a key activity like 'research' or 'archival work', it should be considered a partner. This includes formal partners, media outlets, and resource providers like universities.")
    workspace: Optional[str] = Field(default=None, description="The specified workshop, studio, or space where the artistic creation will take place.")

    # 4. Supporting Documents
    supporting_documents: Optional[SupportingDocument] = Field(default=None, description="A checklist of provided supporting documents.")

class FullAnalysisResponse(BaseModel):
    extracted_data: Application
    synopsis: str = Field(description="A 3-5 sentence, easy-to-read summary of the application in Swedish.")
    keywords: List[str] = Field(description="A comprehensive list of relevant keywords in Swedish for filtering and search. Include keywords from the following categories: 1. Art forms and media (konstnärliga former) 2. Subject matter (ämnesområden)3. Methodology (metoder) 4. Cultural aspects (kulturella aspekter)5. Community engagement Prioritize core artistic and technical terms alongside thematic and contextual keywords.")