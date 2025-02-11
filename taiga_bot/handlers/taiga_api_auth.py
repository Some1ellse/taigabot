"""Authentication handler for Taiga API"""
from datetime import datetime, timedelta
import requests # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
from config.config import (  # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
    TAIGA_BASE_URL,
    TAIGA_USERNAME,
    TAIGA_PASSWORD
    )


class TaigaAuth:
    """Authentication handler for Taiga API"""
    def __init__(self):
        self.base_url = TAIGA_BASE_URL
        self.username = TAIGA_USERNAME
        self.password = TAIGA_PASSWORD
        self.token = None
        self.refresh_token = None
        self.token_expiry = None
        self.token_lifetime = timedelta(hours=24)  # Taiga tokens typically last 24 hours

        # Validate environment variables
        if not all([self.username, self.password]):
            raise ValueError("TAIGA_USERNAME and TAIGA_PASSWORD must be set in .env file")

    def _authenticate(self):
        """Authenticate with Taiga API and get a new token"""
        print("Generating new API token with password auth")
        auth_url = f"{self.base_url}/api/v1/auth"
        payload = {
            "type": "normal",
            "username": self.username,
            "password": self.password
        }

        try:
            auth_response = requests.post(auth_url, json=payload, timeout=30)
            auth_response.raise_for_status()
            auth_data = auth_response.json()


            self.token = auth_data['auth_token']
            self.refresh_token = auth_data['refresh']
            self.token_expiry = datetime.now() + self.token_lifetime

            # Update environment variable
            #os.environ['TAIGA_AUTH_TOKEN'] = self.token
            #set_key('.env', 'TAIGA_AUTH_TOKEN', self.token)

            # Validate the token immediately
            print("Authenticated, validating token...")
            if not self._validate_token():
                raise ValueError("Obtained token failed validation")

            return True

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            self.token = None
            self.token_expiry = None
            return False

    def _validate_token(self):
        """Validate the current auth token by making a test API call"""
        if not self.token:
            return False
        print("Validating API token....")
        auth_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            # Make a lightweight API call to verify token
            auth_response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                headers=auth_headers,
                timeout=30
            )
            auth_data = auth_response.json()
            #print("API token validation response: ", auth_response.status_code)
            if auth_response.status_code != 200:
                return False
            #print(
            #    f"Authenticated as: "
            #    f"{auth_data.get('full_name_display', auth_data.get('username'))}"
            #    )
            return True #auth_response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_token(self):
        """Get a valid authentication token."""
        # If we have a token, verify it's still valid with the API
        if self.token:
            if self._validate_token():
                print("API token is valid, keeping it!")
                return self.token
            print("API token is missing, invalid or expired, refreshing...")

        # If we have a refresh token, try to use it first
        if self.refresh_token:
            print("Refresh token detected, attempting to use it")
            try:
                refresh_url = f"{self.base_url}/api/v1/auth/refresh"
                refresh_response = requests.post(
                    refresh_url,
                    json={"refresh": self.refresh_token},
                    timeout=30
                )
                refresh_response.raise_for_status()

                refresh_data = refresh_response.json()
                self.token = refresh_data['access']
                self.refresh_token = refresh_data['refresh']
                self.token_expiry = datetime.now() + self.token_lifetime

                print("Token refreshed successfully")
                return self.token

            except requests.RequestException as e:
                print(f"Token refresh failed: {e}, falling back to password auth")

        # If refresh failed or we don't have a refresh token, authenticate with username/password
        print("No refresh token, falling back to password auth")
        if not self._authenticate():
            raise ValueError("Authentication failed - check your credentials")
        return self.token

    def get_headers(self):
        """Get headers with valid authentication token"""
        token = self.get_token()
        if not token:
            return None
        return True

#Singleton instance for global use
taiga_auth = TaigaAuth()
#
#if __name__ == "__main__":
#    # Test the authentication
#    try:
#        headers = taiga_auth.get_headers()
#        if headers:
#            print("Authentication successful!")
#            print(f"Token: {taiga_auth.token}")
#        else:
#            print("Failed to obtain authentication token!")
#    except (requests.RequestException, ValueError, KeyError) as e:
#        # Handle specific exceptions as e:
#        print(f"Error during authentication test: {e}")
