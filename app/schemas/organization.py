from pydantic import BaseModel


class OrganizationOut(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True
