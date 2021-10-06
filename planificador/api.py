from django.http import response
import requests
from requests.auth import HTTPBasicAuth


def api_token():
    url = "https://cloudsso.hilti.com/hc/token"
    headers = {
        "Authorization": 'Basic "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5UWXlOemcyTUVRd04wTTNOMFpCTkRVME9FSXlRVEpCTlVFeU9EQTNPVFZHTXpVeU9UTTROZyJ9.eyJodHRwczovL2Nsb3VkLmhpbHRpLmNvbS9jbGllbnRJZCI6IkRRMHQzQ0pUZUNIQzQ0WFpCUTVMWnl4SjNKTndydUNsIiwiaHR0cHM6Ly9jbG91ZC5oaWx0aS5jb20vY3VzdG9tZXJfaWQiOiIxMjI3NjA2MSIsImh0dHBzOi8vY2xvdWQuaGlsdGkuY29tL2xvZ29uSWQiOiJ0ZWNodXNlci1jbC1ybWMtbG15c2hleWhsNmg5YTl1cUBhcGktdXNlci5oaWx0aS5jbG91ZCIsImh0dHBzOi8vY2xvdWQuaGlsdGkuY29tL3VpZCI6ImF1dGgwfDYxMzljODBkMTc4MGU1MDA2YTliZDRkZSIsImlzcyI6Imh0dHBzOi8vY2xvdWRzc28uaGlsdGkuY29tLyIsInN1YiI6ImF1dGgwfDYxMzljODBkMTc4MGU1MDA2YTliZDRkZSIsImF1ZCI6WyJ1cm46aGM6YXBpIiwiaHR0cHM6Ly9oaWx0aS1pZG0tcHJkLmV1LmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MzM0NDY4MTgsImV4cCI6MTYzMzQ1MDQxOCwiYXpwIjoiRFEwdDNDSlRlQ0hDNDRYWkJRNUxaeXhKM0pOd3J1Q2wiLCJzY29wZSI6ImFkZHJlc3MgZW1haWwgSEMuUmVxdWVzdC5BbGxTY29wZXMgb2ZmbGluZV9hY2Nlc3Mgb3BlbmlkIHBob25lIHByb2ZpbGUgVFMuT05UcmFjay5DSVMuRVJQLkFsbCBUUy5PTlRyYWNrLlVuaXRlLkFzc2V0cy5SZWFkIFRTLk9OVHJhY2suVW5pdGUuQXNzZXRzLldyaXRlIFRTLk9OVHJhY2suVW5pdGUuTG9jYXRpb25zLlJlYWQgVFMuT05UcmFjay5Vbml0ZS5Mb2NhdGlvbnMuV3JpdGUgVFMuT05UcmFjay5Vbml0ZS5Xb3JrZXJzLlJlYWQgVFMuT05UcmFjay5Vbml0ZS5Xb3JrZXJzLldyaXRlIiwiZ3R5IjoicGFzc3dvcmQifQ.hKRv9_OFvygzbyK1d4weQZj7QKQQ2yATbrKXpL9jdWjpnwhc8b6h_gKo1ntizdefJvoB2LzNF50d4UpxUkIJxQXD1U_I1pJ02NMmhZhSLXxrhnnRvzfIaBriI4wrO3KnqT71_Cc_ggDmWjx_UUd9DQ_g3qAV5PfY6hxksKUB0NyQWQWy_AoGXaaiKopWhc7qjDWSDsbwEIcON3_dmgJNpMju_zPtmxydsajsV0pHosQ1P1IHXBGIfLTpfvJa_lFjZUvJyDSM68oLl2aX4XynGtN1kcsFyf-wLnmp_ZynxC3Z2llBnK_neXfyiPgEiL7n2P_2ra-JFaL4k1eJ9iu1kw"'
    }
    payload = {
        "grant_type": "password",
        "scope": "HC.Request.ALLScopes",
        "username": "techuser-cl-rmc-lmysheyhl6h9a9uq@api-user.hilti.cloud",
        "password": "+*Y%*JTdqk$e)_2^I^nu!0Q2m7ZmpA&%",
    }
    res = requests.post(
        url,
        headers=headers,
        data=payload,
        auth=HTTPBasicAuth(
            "DQ0t3CJTeCHC44XZBQ5LZyxJ3JNwruCl",
            "CzSkygd1iFAmB4uNhQqi3YHNdVLseRESeJZZHitGeGUtkDTTYyGX-6ONV69JDb62",
        ),
    )
    json = res.json()
    return json["access_token"]


def get_locations(api_token):
    url = "https://cloudapis.hilti.com/ts/ontrack/unite/v1/locations"
    headers = {
        "Authorization": "Bearer {}".format(api_token),
        "Accept": "application/json;odata=verbose",
        "Prefer": "return=representation",
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()["result"]
    else:
        headers = {
            "Authorization": "Bearer {}".format(api_token()),
            "Accept": "application/json;odata=verbose",
            "Prefer": "return=representation",
        }
        res = requests.get(url, headers=headers)
        return res.json()["result"]
