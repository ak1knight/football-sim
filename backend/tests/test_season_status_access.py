import requests

API_URL = "http://localhost:5000/api/season/status"
# Replace with a valid JWT for user1 and a valid season_id for user1 and user2
USER1_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOTNlMDAzMTUtYWZmMy00MmE0LTkzZmUtMDdjMGViZGM3YjQ5IiwidXNlcm5hbWUiOiJha25pZ2h0IiwiZXhwIjoxNzU1MDUzMDc2fQ.ip5ZnEQZLrbcd1NLVOqW7oh0byTirKxEnZSD-tARj9I"
USER2_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOTNlMDAzMTUtYWZmMy00MmE0LTkzZmUtMDdjMGViZGM3YjQ5IiwidXNlcm5hbWUiOiJ1c2VyMiIsImV4cCI6MTc1NTA1MzA3Nn0.5g5ZnEQZLrbcd1NLVOqW7oh0byTirKxEnZSD-tARj9I"
USER1_SEASON_ID = "fdd3a201-1b3b-4e05-9889-d20f640c4312"
USER2_SEASON_ID = "REPLACE_WITH_USER2_SEASON_ID"

def test_status(jwt, season_id):
    headers = {"Authorization": f"Bearer {jwt}"}
    params = {"season_id": season_id}
    resp = requests.get(API_URL, headers=headers, params=params)
    print(f"JWT: {jwt[:10]}..., season_id: {season_id}, status: {resp.status_code}, response: {resp.json()}")

if __name__ == "__main__":
    print("Should succeed (user1 accessing own season):")
    test_status(USER1_JWT, USER1_SEASON_ID)