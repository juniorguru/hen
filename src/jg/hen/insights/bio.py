from githubkit.rest import PublicUser

from jg.hen.signals import insight, on_profile


@insight(on_profile)
async def bio(user: PublicUser) -> str | None:
    return user.bio
