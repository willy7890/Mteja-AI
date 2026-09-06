from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class StockBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=0)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    class_name: str = Field(
        validation_alias=AliasChoices("class", "class_name"),
        serialization_alias="class",
        min_length=1,
        max_length=100,
    )


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    class_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("class", "class_name"),
        serialization_alias="class",
        min_length=1,
        max_length=100,
    )


class StockResponse(StockBase):
    id: int
    organization_id: int
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)