from datetime import datetime
from typing import Annotated
import uuid
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy import BigInteger, func
from sqlalchemy.orm import declarative_base, mapped_column

Base = declarative_base()


uuid_pk = Annotated[uuid.UUID, mapped_column(psql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
bigInt = Annotated[int, mapped_column(BigInteger)]
createdAt = Annotated[datetime, mapped_column(server_default=func.now())]