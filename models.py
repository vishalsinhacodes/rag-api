from pydantic import BaseModel, Field, field_validator

class AskRequest(BaseModel):
    """Schema for a single RAG query."""

    question: str = Field(
        ..., 
        description="The user's question to be answered using local documents.",
        min_length=1,
        max_length=500
    )
    
    @field_validator("question")
    @classmethod
    def question_must_be_valid(cls, v: str) -> str:
        """Strips whitespace and ensures the question is not just spaces."""        
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty")
        
        if len(v) > 500:
            raise ValueError("Question must be under 500 characters")
        
        return v
    
class AskResponse(BaseModel):
    """
    The successful response containing the AI-generated answer 
    and the supporting document fragments.
    """
    answer: str
    sources: list[str]
    
class IngestRequest(BaseModel):
    """
    Data model for batch document ingestion into the vector database.
    
    This handles the cleaning and validation of raw text strings before 
    they are converted into vector embeddings.
    """    
    documents: list[str]
    
    @field_validator("documents")
    @classmethod
    def documents_must_be_valid(cls, v: list[str]) -> list[str]:
        """
        Cleans and validates the document list.
        
        - Ensures the list is not empty.
        - Enforces a batch limit of 50 documents.
        - Removes whitespace and ignores empty strings.
        """        
        if not v:
            raise ValueError("Documents list cannot be empty")
        
        if len(v) > 50:
            raise ValueError("Cannot ingest more than 50 documents at once")
        
        return [doc.strip() for doc in v if doc.strip()]
    
class IngestResponse(BaseModel):
    """
    Confirmation of a successful document ingestion batch.
    
    This model provides the total count of documents processed and 
    a human-readable status message.
    """    
    ingested: int
    message: str