from users.validators import validate_github_url


class GithubUrlCleanMixin:
    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        validate_github_url(github_url)
        return github_url
