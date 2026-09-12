from pydantic import BaseModel, ConfigDict, Field, model_validator


class ItemBase(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None

    @model_validator(mode="after")
    def reject_explicit_null_name(self):
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null")
        return self


class Item(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
