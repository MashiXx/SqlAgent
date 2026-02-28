"""User authentication resolver for SqlAgent"""

from vanna.core.user import UserResolver, User, RequestContext


class SimpleUserResolver(UserResolver):
    """Simple user authentication resolver"""

    async def resolve_user(self, request_context: RequestContext) -> User:
        """Resolve user from request context"""
        # Get user email from cookie or default to guest
        user_email = request_context.get_cookie('vanna_email') or 'guest@example.com'

        # Assign group based on email
        group = 'admin' if user_email == 'admin@example.com' else 'user'

        return User(
            id=user_email,
            email=user_email,
            group_memberships=[group]
        )
