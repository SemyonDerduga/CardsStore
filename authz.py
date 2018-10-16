from aiohttp_security.abc import AbstractAuthorizationPolicy
import bcrypt


class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, user_map):
        super().__init__()
        self.user_map = user_map

    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or "None" if no user exists related to the identity.
        """

        exsist = await self.user_map.execute("get",
                                             str("User:"+identity+":password"))
        if exsist:
            return identity
        return None

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission in the
        current context, else return False.
        """
        return True


async def check_credentials(db, username, password):
    user_password = await db.execute("get", str("User:"+username+":password"))

    if not user_password:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), user_password)
