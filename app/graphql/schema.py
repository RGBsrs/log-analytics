import strawberry
from fastapi import Depends
from strawberry.fastapi import GraphQLRouter
from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.elasticsearch import get_es
from app.graphql.queries import Query
from app.graphql.mutations import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)

async def get_context(
    es: AsyncElasticsearch = Depends(get_es),
    session: AsyncSession = Depends(get_session)
) -> dict:
    return {"es": es, "session": session}

graphql_router = GraphQLRouter(schema, context_getter=get_context)
