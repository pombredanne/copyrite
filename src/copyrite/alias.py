"""Manages aliases for different authors."""

import collections
import typing

from copyrite import vcs

_AliasBase = collections.namedtuple('_AliasBase', 'name mails authoritative_mail')


class Alias(_AliasBase):
    """An author alias

    An alias can be viewed as an authoritative entity under
    which multiple contributions can live. For instance,
    if one user contributed to the project by using multiple e-mails,
    the alias can be used to use only one of those names or another,
    prespecified name.
    """

    def __new__(cls,
                name: str,
                mails: typing.List[str],
                # pylint: disable=bad-whitespace; false positive
                authoritative_mail: typing.Optional[str] = None):

        return _AliasBase.__new__(cls, name, mails, authoritative_mail) # type: ignore; fp


# pylint: disable=invalid-name
_ContributionsIterableType = typing.Iterable[vcs.Contribution]
_AliasContributionGroupType = typing.Dict[vcs.Contribution, Alias]
# pylint: enable=invalid-name


def _find_proper_alias(aliases: typing.List[Alias],
                       contribution: vcs.Contribution) -> typing.Optional[Alias]:

    for candidate_alias in aliases:
        if contribution.mail in candidate_alias.mails:
            # Valid candidate
            return candidate_alias


def _applied_aliases(candidates: _AliasContributionGroupType) -> _ContributionsIterableType:
    for contribution, alias in candidates.items():
        if alias:
            mail = alias.authoritative_mail or contribution.mail
            name = alias.name or contribution.author
            yield contribution._replace(author=name, mail=mail) # type: ignore
        else:
            yield contribution


def apply_aliases(contributions: typing.List[vcs.Contribution],
                  aliases: typing.List[Alias]) -> typing.List[vcs.Contribution]:
    """Apply the aliases over the contributions.

    The function finds all contributions which can live under a given alias
    and tries to apply the alias's information over them.
    """

    candidates = {contribution: _find_proper_alias(aliases, contribution)
                  for contribution in contributions}
    return list(_applied_aliases(candidates))